"""Service for anomaly detection in biddings."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from decimal import Decimal

from src.models import Anomalia, Licitacao, Item, Resultado, Fornecedor
from src.database.connection import get_db


class AnomaliaService:
    """Service for detecting anomalies in bidding processes."""
    
    TIPOS_ANOMALIA = {
        'PRECO_ACIMA_MEDIA': 'Preço acima da média histórica',
        'PRECO_MUITO_ACIMA': 'Preço muito acima da média (>50%)',
        'PRECO_EXTREMO': 'Preço extremamente alto (>100%)',
        'FORNECEDOR_RECORRENTE': 'Mesmo fornecedor vencedor recorrente',
        'BAIXA_COMPETICAO': 'Baixa competição (<3 participantes)',
        'PRAZO_CURTO': 'Prazo muito curto para propostas',
        'VALOR_FRACIONADO': 'Possível fracionamento de valor',
        'EMPRESA_IMPEDIDA': 'Empresa com impedimento no CEIS/CNEP',
        'PRECO_ABAIXO_CUSTO': 'Preço muito abaixo do estimado (possível inexequível)',
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def detectar_anomalias_preco(self, item_id: int) -> List[Anomalia]:
        """Detect price anomalies by comparing with historical data."""
        anomalias = []
        
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.valor_unitario_estimado:
            return anomalias
        
        # Get historical prices for similar items
        historico = self.db.query(
            func.avg(Item.valor_unitario_estimado).label('media'),
            func.stddev(Item.valor_unitario_estimado).label('desvio')
        ).filter(
            and_(
                Item.descricao.ilike(f'%{item.descricao[:50]}%'),
                Item.id != item_id,
                Item.valor_unitario_estimado > 0
            )
        ).first()
        
        if historico and historico.media:
            media = float(historico.media)
            valor = float(item.valor_unitario_estimado)
            desvio_percentual = ((valor - media) / media) * 100
            
            # Detect different severity levels
            if desvio_percentual > 100:
                tipo = 'PRECO_EXTREMO'
                score = 90.0
            elif desvio_percentual > 50:
                tipo = 'PRECO_MUITO_ACIMA'
                score = 70.0
            elif desvio_percentual > 30:
                tipo = 'PRECO_ACIMA_MEDIA'
                score = 50.0
            else:
                return anomalias
            
            anomalia = Anomalia(
                licitacao_id=item.licitacao_id,
                item_id=item_id,
                tipo=tipo,
                descricao=self.TIPOS_ANOMALIA[tipo],
                valor_detectado=item.valor_unitario_estimado,
                valor_referencia=Decimal(str(media)),
                percentual_desvio=Decimal(str(desvio_percentual)),
                score_risco=Decimal(str(score)),
                status='pendente'
            )
            anomalias.append(anomalia)
        
        return anomalias
    
    def detectar_fornecedor_recorrente(
        self, 
        orgao_id: int, 
        periodo_dias: int = 365
    ) -> List[Anomalia]:
        """Detect if the same supplier wins many bids in a row."""
        anomalias = []
        data_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        # Count wins by supplier for this orgao
        vitorias = self.db.query(
            Fornecedor.id,
            Fornecedor.razao_social,
            func.count(Resultado.id).label('total_vitorias')
        ).join(
            Resultado, Resultado.fornecedor_id == Fornecedor.id
        ).join(
            Item, Item.id == Resultado.item_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Licitacao.orgao_id == orgao_id,
                Licitacao.data_publicacao_pncp >= data_inicio
            )
        ).group_by(
            Fornecedor.id, Fornecedor.razao_social
        ).having(
            func.count(Resultado.id) > 10
        ).all()
        
        for vitoria in vitorias:
            # Calculate concentration
            total_licitacoes = self.db.query(func.count(Licitacao.id)).filter(
                and_(
                    Licitacao.orgao_id == orgao_id,
                    Licitacao.data_publicacao_pncp >= data_inicio
                )
            ).scalar()
            
            concentracao = (vitoria.total_vitorias / total_licitacoes * 100) if total_licitacoes > 0 else 0
            
            if concentracao > 30:  # More than 30% concentration
                anomalia = Anomalia(
                    fornecedor_id=vitoria.id,
                    tipo='FORNECEDOR_RECORRENTE',
                    descricao=f'Fornecedor {vitoria.razao_social} venceu {vitoria.total_vitorias} de {total_licitacoes} licitações ({concentracao:.1f}%)',
                    valor_detectado=Decimal(str(vitoria.total_vitorias)),
                    valor_referencia=Decimal(str(total_licitacoes)),
                    percentual_desvio=Decimal(str(concentracao)),
                    score_risco=Decimal(str(min(concentracao, 100))),
                    status='pendente'
                )
                anomalias.append(anomalia)
        
        return anomalias
    
    def detectar_baixa_competicao(self, licitacao_id: int) -> Optional[Anomalia]:
        """Detect biddings with few participants."""
        # Count unique suppliers for this bidding
        num_fornecedores = self.db.query(
            func.count(func.distinct(Resultado.fornecedor_id))
        ).join(
            Item, Item.id == Resultado.item_id
        ).filter(
            Item.licitacao_id == licitacao_id
        ).scalar()
        
        if num_fornecedores and num_fornecedores < 3:
            score = 60.0 if num_fornecedores == 1 else 40.0
            
            return Anomalia(
                licitacao_id=licitacao_id,
                tipo='BAIXA_COMPETICAO',
                descricao=f'Apenas {num_fornecedores} fornecedor(es) participaram',
                valor_detectado=Decimal(str(num_fornecedores)),
                score_risco=Decimal(str(score)),
                status='pendente'
            )
        
        return None
    
    def detectar_prazo_curto(self, licitacao_id: int) -> Optional[Anomalia]:
        """Detect biddings with very short proposal deadline."""
        licitacao = self.db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()
        
        if not licitacao or not licitacao.data_publicacao_pncp or not licitacao.data_abertura_proposta:
            return None
        
        prazo_dias = (licitacao.data_abertura_proposta - licitacao.data_publicacao_pncp).days
        
        if prazo_dias < 5:  # Less than 5 days
            score = 70.0 if prazo_dias < 3 else 50.0
            
            return Anomalia(
                licitacao_id=licitacao_id,
                tipo='PRAZO_CURTO',
                descricao=f'Prazo de apenas {prazo_dias} dias entre publicação e abertura',
                valor_detectado=Decimal(str(prazo_dias)),
                score_risco=Decimal(str(score)),
                status='pendente'
            )
        
        return None
    
    def calcular_score_risco(self, licitacao_id: int) -> float:
        """Calculate risk score from 0 to 100 based on anomalies."""
        anomalias = self.db.query(Anomalia).filter(
            Anomalia.licitacao_id == licitacao_id
        ).all()
        
        if not anomalias:
            return 0.0
        
        # Calculate weighted average of risk scores
        total_score = sum(float(a.score_risco or 0) for a in anomalias)
        return min(total_score / len(anomalias), 100.0)
    
    def executar_analise_completa(self, licitacao_id: Optional[int] = None) -> List[Anomalia]:
        """Execute complete anomaly analysis."""
        anomalias = []
        
        # If specific licitacao_id, analyze only that one
        if licitacao_id:
            licitacoes = [self.db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()]
        else:
            # Analyze recent biddings (last 30 days)
            data_limite = datetime.now() - timedelta(days=30)
            licitacoes = self.db.query(Licitacao).filter(
                Licitacao.data_publicacao_pncp >= data_limite
            ).all()
        
        for licitacao in licitacoes:
            if not licitacao:
                continue
            
            # Check short deadline
            prazo_anomalia = self.detectar_prazo_curto(licitacao.id)
            if prazo_anomalia:
                anomalias.append(prazo_anomalia)
            
            # Check low competition
            competicao_anomalia = self.detectar_baixa_competicao(licitacao.id)
            if competicao_anomalia:
                anomalias.append(competicao_anomalia)
            
            # Check price anomalies for items
            for item in licitacao.itens:
                preco_anomalias = self.detectar_anomalias_preco(item.id)
                anomalias.extend(preco_anomalias)
        
        # Save anomalies to database
        for anomalia in anomalias:
            # Check if already exists
            existe = self.db.query(Anomalia).filter(
                and_(
                    Anomalia.licitacao_id == anomalia.licitacao_id,
                    Anomalia.item_id == anomalia.item_id,
                    Anomalia.tipo == anomalia.tipo
                )
            ).first()
            
            if not existe:
                self.db.add(anomalia)
        
        self.db.commit()
        
        return anomalias
