"""API routes for dashboard statistics."""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case

from src.database.connection import get_db
from src.models import Licitacao, Item, Fornecedor, Resultado, Municipio, Anomalia, AlertaDisparado


router = APIRouter(prefix="/api/v1/estatisticas", tags=["Estatísticas"])


@router.get("/kpis", response_model=dict)
async def kpis_dashboard(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get main KPIs for dashboard."""
    # Build base query
    query = db.query(Licitacao)
    
    # Apply date filters
    if data_inicio:
        query = query.filter(Licitacao.data_publicacao_pncp >= datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(Licitacao.data_publicacao_pncp <= datetime.fromisoformat(data_fim))
    if municipio_id:
        query = query.filter(Licitacao.municipio_id == municipio_id)
    
    # Total biddings
    total_licitacoes = query.count()
    
    # Open biddings
    hoje = datetime.now()
    licitacoes_abertas = query.filter(
        and_(
            Licitacao.data_abertura_proposta.isnot(None),
            Licitacao.data_abertura_proposta <= hoje,
            Licitacao.data_encerramento_proposta >= hoje
        )
    ).count()
    
    # Total estimated value
    valor_total_estimado = query.with_entities(
        func.sum(Licitacao.valor_total_estimado)
    ).scalar() or 0
    
    # Total homologated value
    valor_total_homologado = query.with_entities(
        func.sum(Licitacao.valor_total_homologado)
    ).scalar() or 0
    
    # Economy generated
    economia_gerada = float(valor_total_estimado) - float(valor_total_homologado)
    economia_percentual = (economia_gerada / float(valor_total_estimado) * 100) if valor_total_estimado > 0 else 0
    
    # Pending alerts
    alertas_pendentes = db.query(AlertaDisparado).filter(
        AlertaDisparado.enviado == False
    ).count()
    
    # Detected anomalies
    anomalias_detectadas = db.query(Anomalia).filter(
        Anomalia.status == 'pendente'
    ).count()
    
    return {
        'total_licitacoes': total_licitacoes,
        'licitacoes_abertas': licitacoes_abertas,
        'valor_total_estimado': float(valor_total_estimado),
        'valor_total_homologado': float(valor_total_homologado),
        'economia_gerada': {
            'valor': economia_gerada,
            'percentual': round(economia_percentual, 2)
        },
        'alertas_pendentes': alertas_pendentes,
        'anomalias_detectadas': anomalias_detectadas
    }


@router.get("/por-mes", response_model=dict)
async def licitacoes_por_mes(
    meses: int = Query(12, ge=1, le=36),
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get biddings count by month."""
    from sqlalchemy import extract
    
    # Calculate date range
    data_limite = datetime.now() - timedelta(days=meses * 30)
    
    # Build query
    query = db.query(
        extract('year', Licitacao.data_publicacao_pncp).label('ano'),
        extract('month', Licitacao.data_publicacao_pncp).label('mes'),
        func.count(Licitacao.id).label('total'),
        func.sum(Licitacao.valor_total_estimado).label('valor_total')
    ).filter(
        Licitacao.data_publicacao_pncp >= data_limite
    )
    
    if municipio_id:
        query = query.filter(Licitacao.municipio_id == municipio_id)
    
    resultados = query.group_by('ano', 'mes').order_by('ano', 'mes').all()
    
    # Format results
    series = []
    for r in resultados:
        series.append({
            'periodo': f"{int(r.ano)}-{int(r.mes):02d}",
            'total': r.total,
            'valor_total': float(r.valor_total) if r.valor_total else 0
        })
    
    return {
        'meses': meses,
        'series': series
    }


@router.get("/por-modalidade", response_model=dict)
async def distribuicao_modalidade(
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get biddings distribution by modality."""
    query = db.query(
        Licitacao.modalidade_nome,
        func.count(Licitacao.id).label('total'),
        func.sum(Licitacao.valor_total_estimado).label('valor_total')
    )
    
    if municipio_id:
        query = query.filter(Licitacao.municipio_id == municipio_id)
    
    resultados = query.group_by(Licitacao.modalidade_nome).all()
    
    # Format results
    distribuicao = []
    for r in resultados:
        if r.modalidade_nome:
            distribuicao.append({
                'modalidade': r.modalidade_nome,
                'total': r.total,
                'valor_total': float(r.valor_total) if r.valor_total else 0
            })
    
    return {
        'distribuicao': distribuicao
    }


@router.get("/top-municipios", response_model=dict)
async def top_municipios(
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get top municipalities by value."""
    resultados = db.query(
        Municipio.id,
        Municipio.municipio,
        Municipio.uf,
        func.count(Licitacao.id).label('total_licitacoes'),
        func.sum(Licitacao.valor_total_estimado).label('valor_total')
    ).join(
        Licitacao, Licitacao.municipio_id == Municipio.id
    ).group_by(
        Municipio.id, Municipio.municipio, Municipio.uf
    ).order_by(
        func.sum(Licitacao.valor_total_estimado).desc()
    ).limit(limite).all()
    
    # Format results
    top = []
    for r in resultados:
        top.append({
            'municipio_id': r.id,
            'municipio': r.municipio,
            'uf': r.uf,
            'total_licitacoes': r.total_licitacoes,
            'valor_total': float(r.valor_total) if r.valor_total else 0
        })
    
    return {
        'top': top,
        'limite': limite
    }


@router.get("/top-fornecedores", response_model=dict)
async def top_fornecedores(
    limite: int = Query(10, ge=1, le=50),
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get top suppliers by value."""
    query = db.query(
        Fornecedor.id,
        Fornecedor.razao_social,
        Fornecedor.porte_fornecedor_nome,
        func.count(Resultado.id).label('total_vitorias'),
        func.sum(Resultado.valor_total_homologado).label('valor_total')
    ).join(
        Resultado, Resultado.fornecedor_id == Fornecedor.id
    )
    
    if municipio_id:
        query = query.join(Item).join(Licitacao).filter(Licitacao.municipio_id == municipio_id)
    
    resultados = query.group_by(
        Fornecedor.id, Fornecedor.razao_social, Fornecedor.porte_fornecedor_nome
    ).order_by(
        func.sum(Resultado.valor_total_homologado).desc()
    ).limit(limite).all()
    
    # Format results
    top = []
    for r in resultados:
        top.append({
            'fornecedor_id': r.id,
            'razao_social': r.razao_social,
            'porte': r.porte_fornecedor_nome,
            'total_vitorias': r.total_vitorias,
            'valor_total': float(r.valor_total) if r.valor_total else 0
        })
    
    return {
        'top': top,
        'limite': limite
    }


@router.get("/economia-por-periodo", response_model=dict)
async def economia_por_periodo(
    meses: int = Query(12, ge=1, le=36),
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get savings by period."""
    from sqlalchemy import extract
    
    # Calculate date range
    data_limite = datetime.now() - timedelta(days=meses * 30)
    
    # Build query
    query = db.query(
        extract('year', Licitacao.data_publicacao_pncp).label('ano'),
        extract('month', Licitacao.data_publicacao_pncp).label('mes'),
        func.sum(Licitacao.valor_total_estimado).label('estimado'),
        func.sum(Licitacao.valor_total_homologado).label('homologado')
    ).filter(
        and_(
            Licitacao.data_publicacao_pncp >= data_limite,
            Licitacao.valor_total_estimado.isnot(None),
            Licitacao.valor_total_homologado.isnot(None)
        )
    )
    
    if municipio_id:
        query = query.filter(Licitacao.municipio_id == municipio_id)
    
    resultados = query.group_by('ano', 'mes').order_by('ano', 'mes').all()
    
    # Format results
    series = []
    for r in resultados:
        estimado = float(r.estimado) if r.estimado else 0
        homologado = float(r.homologado) if r.homologado else 0
        economia = estimado - homologado
        economia_percentual = (economia / estimado * 100) if estimado > 0 else 0
        
        series.append({
            'periodo': f"{int(r.ano)}-{int(r.mes):02d}",
            'estimado': estimado,
            'homologado': homologado,
            'economia': economia,
            'economia_percentual': round(economia_percentual, 2)
        })
    
    return {
        'meses': meses,
        'series': series
    }


@router.get("/ultimas-licitacoes", response_model=dict)
async def ultimas_licitacoes(
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get latest published biddings."""
    licitacoes = db.query(Licitacao).order_by(
        Licitacao.data_publicacao_pncp.desc()
    ).limit(limite).all()
    
    # Format results
    items = []
    for lic in licitacoes:
        items.append({
            'id': lic.id,
            'numero_compra': lic.numero_compra,
            'objeto_compra': lic.objeto_compra[:200] if lic.objeto_compra else None,
            'modalidade_nome': lic.modalidade_nome,
            'valor_total_estimado': float(lic.valor_total_estimado) if lic.valor_total_estimado else None,
            'data_publicacao_pncp': lic.data_publicacao_pncp.isoformat() if lic.data_publicacao_pncp else None,
            'data_abertura_proposta': lic.data_abertura_proposta.isoformat() if lic.data_abertura_proposta else None,
            'municipio_id': lic.municipio_id
        })
    
    return {
        'items': items,
        'total': len(items)
    }


@router.get("/proximas-aberturas", response_model=dict)
async def proximas_aberturas(
    dias: int = Query(7, ge=1, le=30),
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get upcoming bidding openings."""
    hoje = datetime.now()
    data_limite = hoje + timedelta(days=dias)
    
    licitacoes = db.query(Licitacao).filter(
        and_(
            Licitacao.data_abertura_proposta >= hoje,
            Licitacao.data_abertura_proposta <= data_limite
        )
    ).order_by(
        Licitacao.data_abertura_proposta
    ).limit(limite).all()
    
    # Format results
    items = []
    for lic in licitacoes:
        items.append({
            'id': lic.id,
            'numero_compra': lic.numero_compra,
            'objeto_compra': lic.objeto_compra[:200] if lic.objeto_compra else None,
            'modalidade_nome': lic.modalidade_nome,
            'valor_total_estimado': float(lic.valor_total_estimado) if lic.valor_total_estimado else None,
            'data_abertura_proposta': lic.data_abertura_proposta.isoformat() if lic.data_abertura_proposta else None,
            'municipio_id': lic.municipio_id
        })
    
    return {
        'items': items,
        'total': len(items),
        'dias': dias
    }
