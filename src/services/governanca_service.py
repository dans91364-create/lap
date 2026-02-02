"""Service for governance analysis and KPIs."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from decimal import Decimal

from src.models import (
    GovernancaMunicipio, Licitacao, Municipio, Fornecedor, 
    Resultado, Item
)


class GovernancaService:
    """Service for governance analysis and KPIs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_indice_transparencia(self, municipio_id: int) -> float:
        """Calculate transparency index (0-100) based on data completeness."""
        # Get biddings from this municipality
        licitacoes = self.db.query(Licitacao).filter(
            Licitacao.municipio_id == municipio_id
        ).all()
        
        if not licitacoes:
            return 0.0
        
        total_campos = 0
        campos_preenchidos = 0
        
        # Essential fields to check
        campos_essenciais = [
            'objeto_compra', 'valor_total_estimado', 'data_publicacao_pncp',
            'data_abertura_proposta', 'modalidade_nome', 'amparo_legal_nome',
            'link_sistema_origem'
        ]
        
        for licitacao in licitacoes:
            for campo in campos_essenciais:
                total_campos += 1
                if getattr(licitacao, campo):
                    campos_preenchidos += 1
        
        if total_campos == 0:
            return 0.0
        
        return (campos_preenchidos / total_campos) * 100
    
    def calcular_taxa_sucesso(self, municipio_id: int, periodo: str = None) -> float:
        """Calculate success rate: % of completed vs failed/deserted biddings."""
        query = self.db.query(Licitacao).filter(
            Licitacao.municipio_id == municipio_id
        )
        
        if periodo:
            # periodo format: YYYY-MM
            ano, mes = periodo.split('-')
            inicio = datetime(int(ano), int(mes), 1)
            if int(mes) == 12:
                fim = datetime(int(ano) + 1, 1, 1)
            else:
                fim = datetime(int(ano), int(mes) + 1, 1)
            
            query = query.filter(
                and_(
                    Licitacao.data_publicacao_pncp >= inicio,
                    Licitacao.data_publicacao_pncp < fim
                )
            )
        
        total = query.count()
        
        if total == 0:
            return 0.0
        
        # Count biddings with results (considered successful)
        com_resultado = query.filter(Licitacao.existe_resultado == True).count()
        
        return (com_resultado / total) * 100
    
    def calcular_tempo_medio_processo(self, municipio_id: int) -> int:
        """Calculate average days between publication and homologation."""
        # Get biddings with both dates
        licitacoes = self.db.query(Licitacao).filter(
            and_(
                Licitacao.municipio_id == municipio_id,
                Licitacao.data_publicacao_pncp.isnot(None),
                Licitacao.existe_resultado == True
            )
        ).all()
        
        if not licitacoes:
            return 0
        
        total_dias = 0
        count = 0
        
        for licitacao in licitacoes:
            # Use data_atualizacao as proxy for homologation date
            if licitacao.data_atualizacao:
                dias = (licitacao.data_atualizacao - licitacao.data_publicacao_pncp).days
                if dias > 0:
                    total_dias += dias
                    count += 1
        
        return total_dias // count if count > 0 else 0
    
    def calcular_indice_concentracao_hhi(self, municipio_id: int) -> float:
        """Calculate Herfindahl-Hirschman Index for market concentration."""
        # Get total value won by each supplier
        resultados = self.db.query(
            Fornecedor.id,
            func.sum(Resultado.valor_total_homologado).label('total_valor')
        ).join(
            Resultado, Resultado.fornecedor_id == Fornecedor.id
        ).join(
            Item, Item.id == Resultado.item_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Licitacao.municipio_id == municipio_id,
                Resultado.valor_total_homologado.isnot(None)
            )
        ).group_by(
            Fornecedor.id
        ).all()
        
        if not resultados:
            return 0.0
        
        # Calculate total market value
        valor_total = sum(float(r.total_valor or 0) for r in resultados)
        
        if valor_total == 0:
            return 0.0
        
        # Calculate HHI: sum of squared market shares
        hhi = 0.0
        for resultado in resultados:
            market_share = (float(resultado.total_valor or 0) / valor_total) * 100
            hhi += market_share ** 2
        
        return hhi
    
    def calcular_participacao_meepp(self, municipio_id: int) -> float:
        """Calculate % of ME/EPP wins."""
        # Count total wins
        total_vitorias = self.db.query(func.count(Resultado.id)).join(
            Item, Item.id == Resultado.item_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            Licitacao.municipio_id == municipio_id
        ).scalar()
        
        if not total_vitorias or total_vitorias == 0:
            return 0.0
        
        # Count ME/EPP wins
        vitorias_meepp = self.db.query(func.count(Resultado.id)).join(
            Fornecedor, Fornecedor.id == Resultado.fornecedor_id
        ).join(
            Item, Item.id == Resultado.item_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Licitacao.municipio_id == municipio_id,
                Fornecedor.porte_fornecedor_nome.in_(['ME', 'EPP'])
            )
        ).scalar()
        
        return (vitorias_meepp / total_vitorias) * 100 if vitorias_meepp else 0.0
    
    def calcular_economia_media(self, municipio_id: int) -> float:
        """Calculate average % savings (estimated vs homologated)."""
        # Get biddings with both values
        licitacoes = self.db.query(
            Licitacao.valor_total_estimado,
            Licitacao.valor_total_homologado
        ).filter(
            and_(
                Licitacao.municipio_id == municipio_id,
                Licitacao.valor_total_estimado.isnot(None),
                Licitacao.valor_total_homologado.isnot(None),
                Licitacao.valor_total_estimado > 0
            )
        ).all()
        
        if not licitacoes:
            return 0.0
        
        economias = []
        for lic in licitacoes:
            estimado = float(lic.valor_total_estimado)
            homologado = float(lic.valor_total_homologado)
            economia = ((estimado - homologado) / estimado) * 100
            economias.append(economia)
        
        return sum(economias) / len(economias) if economias else 0.0
    
    def gerar_ranking_municipios(self) -> List[Dict[str, Any]]:
        """Generate ranking of municipalities by governance."""
        municipios = self.db.query(Municipio).all()
        
        ranking = []
        for municipio in municipios:
            score = self._calcular_score_governanca(municipio.id)
            
            ranking.append({
                'municipio_id': municipio.id,
                'municipio': municipio.municipio,
                'uf': municipio.uf,
                'score_governanca': score,
                'indice_transparencia': self.calcular_indice_transparencia(municipio.id),
                'taxa_sucesso': self.calcular_taxa_sucesso(municipio.id),
                'participacao_meepp': self.calcular_participacao_meepp(municipio.id),
                'economia_media': self.calcular_economia_media(municipio.id)
            })
        
        # Sort by governance score
        ranking.sort(key=lambda x: x['score_governanca'], reverse=True)
        
        return ranking
    
    def _calcular_score_governanca(self, municipio_id: int) -> float:
        """Calculate overall governance score (0-100)."""
        # Weighted average of different indicators
        transparencia = self.calcular_indice_transparencia(municipio_id)
        taxa_sucesso = self.calcular_taxa_sucesso(municipio_id)
        participacao_meepp = self.calcular_participacao_meepp(municipio_id)
        economia = max(0, min(100, self.calcular_economia_media(municipio_id)))
        
        # HHI: lower is better, normalize to 0-100 (10000 = monopoly)
        hhi = self.calcular_indice_concentracao_hhi(municipio_id)
        hhi_score = max(0, 100 - (hhi / 100))
        
        # Weighted score
        score = (
            transparencia * 0.3 +
            taxa_sucesso * 0.25 +
            hhi_score * 0.2 +
            participacao_meepp * 0.15 +
            economia * 0.1
        )
        
        return round(score, 2)
    
    def gerar_relatorio_governanca(self, municipio_id: int, periodo: str = None) -> Dict[str, Any]:
        """Generate complete governance report."""
        municipio = self.db.query(Municipio).filter(Municipio.id == municipio_id).first()
        
        if not municipio:
            return {}
        
        return {
            'municipio': {
                'id': municipio.id,
                'nome': municipio.municipio,
                'uf': municipio.uf,
                'codigo_ibge': municipio.codigo_ibge
            },
            'periodo': periodo,
            'kpis': {
                'indice_transparencia': self.calcular_indice_transparencia(municipio_id),
                'taxa_sucesso': self.calcular_taxa_sucesso(municipio_id, periodo),
                'tempo_medio_dias': self.calcular_tempo_medio_processo(municipio_id),
                'indice_hhi': self.calcular_indice_concentracao_hhi(municipio_id),
                'participacao_meepp': self.calcular_participacao_meepp(municipio_id),
                'economia_media': self.calcular_economia_media(municipio_id)
            },
            'score_governanca': self._calcular_score_governanca(municipio_id),
            'gerado_em': datetime.now().isoformat()
        }
    
    def atualizar_governanca_periodo(self, municipio_id: int = None, periodo: str = None):
        """Update governance data for a period."""
        if not periodo:
            # Use current month
            periodo = datetime.now().strftime('%Y-%m')
        
        municipios = [municipio_id] if municipio_id else [m.id for m in self.db.query(Municipio).all()]
        
        for mun_id in municipios:
            # Check if already exists
            existe = self.db.query(GovernancaMunicipio).filter(
                and_(
                    GovernancaMunicipio.municipio_id == mun_id,
                    GovernancaMunicipio.periodo == periodo
                )
            ).first()
            
            # Count total biddings in period
            ano, mes = periodo.split('-')
            inicio = datetime(int(ano), int(mes), 1)
            if int(mes) == 12:
                fim = datetime(int(ano) + 1, 1, 1)
            else:
                fim = datetime(int(ano), int(mes) + 1, 1)
            
            total_licitacoes = self.db.query(func.count(Licitacao.id)).filter(
                and_(
                    Licitacao.municipio_id == mun_id,
                    Licitacao.data_publicacao_pncp >= inicio,
                    Licitacao.data_publicacao_pncp < fim
                )
            ).scalar()
            
            valor_total = self.db.query(
                func.sum(Licitacao.valor_total_estimado)
            ).filter(
                and_(
                    Licitacao.municipio_id == mun_id,
                    Licitacao.data_publicacao_pncp >= inicio,
                    Licitacao.data_publicacao_pncp < fim
                )
            ).scalar()
            
            if existe:
                existe.indice_transparencia = Decimal(str(self.calcular_indice_transparencia(mun_id)))
                existe.taxa_sucesso = Decimal(str(self.calcular_taxa_sucesso(mun_id, periodo)))
                existe.tempo_medio_dias = self.calcular_tempo_medio_processo(mun_id)
                existe.indice_hhi = Decimal(str(self.calcular_indice_concentracao_hhi(mun_id)))
                existe.participacao_meepp = Decimal(str(self.calcular_participacao_meepp(mun_id)))
                existe.economia_media = Decimal(str(self.calcular_economia_media(mun_id)))
                existe.total_licitacoes = total_licitacoes
                existe.valor_total = valor_total
                existe.updated_at = datetime.now()
            else:
                governanca = GovernancaMunicipio(
                    municipio_id=mun_id,
                    periodo=periodo,
                    indice_transparencia=Decimal(str(self.calcular_indice_transparencia(mun_id))),
                    taxa_sucesso=Decimal(str(self.calcular_taxa_sucesso(mun_id, periodo))),
                    tempo_medio_dias=self.calcular_tempo_medio_processo(mun_id),
                    indice_hhi=Decimal(str(self.calcular_indice_concentracao_hhi(mun_id))),
                    participacao_meepp=Decimal(str(self.calcular_participacao_meepp(mun_id))),
                    economia_media=Decimal(str(self.calcular_economia_media(mun_id))),
                    total_licitacoes=total_licitacoes,
                    valor_total=valor_total
                )
                self.db.add(governanca)
        
        self.db.commit()
