"""Service for statistical price analysis."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from decimal import Decimal
import statistics

from src.models import Item, Licitacao, Resultado


class AnalisePrecoService:
    """Service for statistical price analysis."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_estatisticas_item(
        self, 
        descricao: str, 
        periodo_meses: int = 24
    ) -> Dict[str, Any]:
        """Calculate price statistics for an item."""
        # Calculate date range
        data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
        
        # Get historical prices
        precos_query = self.db.query(
            Item.valor_unitario_estimado
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Item.descricao.ilike(f'%{descricao}%'),
                Item.valor_unitario_estimado.isnot(None),
                Item.valor_unitario_estimado > 0,
                Licitacao.data_publicacao_pncp >= data_limite
            )
        ).all()
        
        if not precos_query:
            return {
                'descricao': descricao,
                'periodo_meses': periodo_meses,
                'total_registros': 0,
                'estatisticas': None
            }
        
        precos = [float(p.valor_unitario_estimado) for p in precos_query]
        
        # Calculate statistics
        media = statistics.mean(precos)
        mediana = statistics.median(precos)
        desvio_padrao = statistics.stdev(precos) if len(precos) > 1 else 0
        minimo = min(precos)
        maximo = max(precos)
        
        # Calculate quartiles
        q1 = statistics.quantiles(precos, n=4)[0] if len(precos) >= 4 else minimo
        q3 = statistics.quantiles(precos, n=4)[2] if len(precos) >= 4 else maximo
        
        return {
            'descricao': descricao,
            'periodo_meses': periodo_meses,
            'total_registros': len(precos),
            'estatisticas': {
                'media': round(media, 2),
                'mediana': round(mediana, 2),
                'desvio_padrao': round(desvio_padrao, 2),
                'minimo': round(minimo, 2),
                'maximo': round(maximo, 2),
                'q1': round(q1, 2),
                'q3': round(q3, 2),
                'iqr': round(q3 - q1, 2)
            }
        }
    
    def comparar_preco_historico(self, item_id: int) -> Dict[str, Any]:
        """Compare item price with historical data."""
        item = self.db.query(Item).filter(Item.id == item_id).first()
        
        if not item or not item.valor_unitario_estimado:
            return {
                'item_id': item_id,
                'comparacao': None
            }
        
        # Get statistics for similar items
        stats = self.calcular_estatisticas_item(item.descricao[:100])
        
        if not stats['estatisticas']:
            return {
                'item_id': item_id,
                'valor_item': float(item.valor_unitario_estimado),
                'comparacao': None
            }
        
        valor = float(item.valor_unitario_estimado)
        media = stats['estatisticas']['media']
        desvio = stats['estatisticas']['desvio_padrao']
        
        # Calculate Z-score
        z_score = (valor - media) / desvio if desvio > 0 else 0
        
        # Calculate percentage difference
        diff_percentual = ((valor - media) / media) * 100 if media > 0 else 0
        
        # Classify price
        if z_score > 2:
            classificacao = 'muito_acima'
        elif z_score > 1:
            classificacao = 'acima'
        elif z_score < -2:
            classificacao = 'muito_abaixo'
        elif z_score < -1:
            classificacao = 'abaixo'
        else:
            classificacao = 'normal'
        
        return {
            'item_id': item_id,
            'valor_item': valor,
            'estatisticas_historico': stats['estatisticas'],
            'comparacao': {
                'z_score': round(z_score, 2),
                'diferenca_percentual': round(diff_percentual, 2),
                'classificacao': classificacao,
                'total_registros': stats['total_registros']
            }
        }
    
    def benchmark_regional(self, descricao: str) -> Dict[str, Any]:
        """Compare prices between municipalities in the region."""
        # Get prices grouped by municipality
        resultados = self.db.query(
            Licitacao.municipio_id,
            func.avg(Item.valor_unitario_estimado).label('preco_medio'),
            func.count(Item.id).label('total_itens')
        ).join(
            Item, Item.licitacao_id == Licitacao.id
        ).filter(
            and_(
                Item.descricao.ilike(f'%{descricao}%'),
                Item.valor_unitario_estimado.isnot(None),
                Item.valor_unitario_estimado > 0
            )
        ).group_by(
            Licitacao.municipio_id
        ).all()
        
        if not resultados:
            return {
                'descricao': descricao,
                'benchmark': []
            }
        
        # Calculate overall average
        precos_medios = [float(r.preco_medio) for r in resultados]
        media_geral = statistics.mean(precos_medios)
        
        benchmark = []
        for resultado in resultados:
            preco_medio = float(resultado.preco_medio)
            diff_percentual = ((preco_medio - media_geral) / media_geral) * 100
            
            benchmark.append({
                'municipio_id': resultado.municipio_id,
                'preco_medio': round(preco_medio, 2),
                'total_itens': resultado.total_itens,
                'diferenca_media_geral': round(diff_percentual, 2)
            })
        
        # Sort by price
        benchmark.sort(key=lambda x: x['preco_medio'])
        
        return {
            'descricao': descricao,
            'media_geral': round(media_geral, 2),
            'benchmark': benchmark
        }
    
    def detectar_outliers(self, descricao: str) -> List[Dict[str, Any]]:
        """Detect price outliers using IQR method."""
        stats = self.calcular_estatisticas_item(descricao)
        
        if not stats['estatisticas']:
            return []
        
        q1 = stats['estatisticas']['q1']
        q3 = stats['estatisticas']['q3']
        iqr = stats['estatisticas']['iqr']
        
        # Define outlier boundaries
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Get items outside boundaries
        outliers_query = self.db.query(
            Item.id,
            Item.descricao,
            Item.valor_unitario_estimado,
            Licitacao.numero_compra,
            Licitacao.municipio_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Item.descricao.ilike(f'%{descricao}%'),
                Item.valor_unitario_estimado.isnot(None),
                or_(
                    Item.valor_unitario_estimado < lower_bound,
                    Item.valor_unitario_estimado > upper_bound
                )
            )
        ).all()
        
        outliers = []
        for item in outliers_query:
            valor = float(item.valor_unitario_estimado)
            tipo = 'acima' if valor > upper_bound else 'abaixo'
            
            outliers.append({
                'item_id': item.id,
                'descricao': item.descricao[:100],
                'valor': valor,
                'numero_compra': item.numero_compra,
                'municipio_id': item.municipio_id,
                'tipo_outlier': tipo,
                'limite_inferior': round(lower_bound, 2),
                'limite_superior': round(upper_bound, 2)
            })
        
        return outliers
    
    def sugerir_preco_referencia(self, descricao: str) -> Dict[str, Any]:
        """Suggest reference price based on historical data."""
        stats = self.calcular_estatisticas_item(descricao)
        
        if not stats['estatisticas']:
            return {
                'descricao': descricao,
                'preco_sugerido': None
            }
        
        # Use median as reference price (more robust to outliers)
        preco_sugerido = stats['estatisticas']['mediana']
        
        # Calculate confidence interval (using median ± 1 std dev as approximation)
        desvio = stats['estatisticas']['desvio_padrao']
        intervalo_min = max(0, preco_sugerido - desvio)
        intervalo_max = preco_sugerido + desvio
        
        return {
            'descricao': descricao,
            'preco_sugerido': round(preco_sugerido, 2),
            'intervalo_confianca': {
                'minimo': round(intervalo_min, 2),
                'maximo': round(intervalo_max, 2)
            },
            'estatisticas': stats['estatisticas'],
            'total_registros': stats['total_registros']
        }
    
    def analisar_tendencia(self, descricao: str, periodo_meses: int = 12) -> Dict[str, Any]:
        """Analyze price trend (rising, stable, falling)."""
        # Get historical prices with dates
        data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
        
        precos_query = self.db.query(
            Item.valor_unitario_estimado,
            Licitacao.data_publicacao_pncp
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Item.descricao.ilike(f'%{descricao}%'),
                Item.valor_unitario_estimado.isnot(None),
                Item.valor_unitario_estimado > 0,
                Licitacao.data_publicacao_pncp >= data_limite
            )
        ).order_by(
            Licitacao.data_publicacao_pncp
        ).all()
        
        if len(precos_query) < 2:
            return {
                'descricao': descricao,
                'tendencia': None
            }
        
        # Simple linear regression
        precos = [float(p.valor_unitario_estimado) for p in precos_query]
        
        # Calculate trend: compare first half with second half
        meio = len(precos) // 2
        media_primeira_metade = statistics.mean(precos[:meio])
        media_segunda_metade = statistics.mean(precos[meio:])
        
        variacao_percentual = ((media_segunda_metade - media_primeira_metade) / media_primeira_metade) * 100
        
        # Classify trend
        if variacao_percentual > 10:
            tendencia = 'subindo'
        elif variacao_percentual < -10:
            tendencia = 'descendo'
        else:
            tendencia = 'estavel'
        
        return {
            'descricao': descricao,
            'periodo_meses': periodo_meses,
            'total_registros': len(precos),
            'tendencia': tendencia,
            'variacao_percentual': round(variacao_percentual, 2),
            'preco_medio_inicio': round(media_primeira_metade, 2),
            'preco_medio_fim': round(media_segunda_metade, 2)
        }
    
    def historico_precos_timeline(
        self, 
        descricao: str, 
        periodo_meses: int = 12
    ) -> List[Dict[str, Any]]:
        """Get price timeline for charts."""
        data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
        
        precos = self.db.query(
            Item.id,
            Item.valor_unitario_estimado,
            Licitacao.data_publicacao_pncp,
            Licitacao.numero_compra,
            Licitacao.municipio_id
        ).join(
            Licitacao, Licitacao.id == Item.licitacao_id
        ).filter(
            and_(
                Item.descricao.ilike(f'%{descricao}%'),
                Item.valor_unitario_estimado.isnot(None),
                Item.valor_unitario_estimado > 0,
                Licitacao.data_publicacao_pncp >= data_limite
            )
        ).order_by(
            Licitacao.data_publicacao_pncp
        ).all()
        
        timeline = []
        for preco in precos:
            timeline.append({
                'item_id': preco.id,
                'valor': float(preco.valor_unitario_estimado),
                'data': preco.data_publicacao_pncp.isoformat() if preco.data_publicacao_pncp else None,
                'numero_compra': preco.numero_compra,
                'municipio_id': preco.municipio_id
            })
        
        return timeline
