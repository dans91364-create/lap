"""API routes for anomaly detection."""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.database.connection import get_db
from src.models import Anomalia
from src.services.anomalia_service import AnomaliaService
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/anomalias", tags=["Anomalias"])


class AnomaliaResponse(BaseModel):
    id: int
    licitacao_id: Optional[int]
    item_id: Optional[int]
    fornecedor_id: Optional[int]
    tipo: str
    descricao: Optional[str]
    valor_detectado: Optional[float]
    valor_referencia: Optional[float]
    percentual_desvio: Optional[float]
    score_risco: Optional[float]
    status: str
    observacoes: Optional[str]
    analisado_por: Optional[str]
    analisado_em: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str
    observacoes: Optional[str] = None
    analisado_por: Optional[str] = None


@router.get("/", response_model=dict)
async def listar_anomalias(
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    municipio_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List detected anomalies with filters."""
    # Build query
    query = db.query(Anomalia)
    
    # Apply filters
    if tipo:
        query = query.filter(Anomalia.tipo == tipo)
    
    if status:
        query = query.filter(Anomalia.status == status)
    
    if municipio_id:
        from src.models import Licitacao
        query = query.join(Licitacao).filter(Licitacao.municipio_id == municipio_id)
    
    if data_inicio:
        query = query.filter(Anomalia.created_at >= data_inicio)
    
    if data_fim:
        query = query.filter(Anomalia.created_at <= data_fim)
    
    # Count total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    anomalias = query.order_by(Anomalia.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Convert to dict
    items = []
    for anomalia in anomalias:
        items.append({
            'id': anomalia.id,
            'licitacao_id': anomalia.licitacao_id,
            'item_id': anomalia.item_id,
            'fornecedor_id': anomalia.fornecedor_id,
            'tipo': anomalia.tipo,
            'descricao': anomalia.descricao,
            'valor_detectado': float(anomalia.valor_detectado) if anomalia.valor_detectado else None,
            'valor_referencia': float(anomalia.valor_referencia) if anomalia.valor_referencia else None,
            'percentual_desvio': float(anomalia.percentual_desvio) if anomalia.percentual_desvio else None,
            'score_risco': float(anomalia.score_risco) if anomalia.score_risco else None,
            'status': anomalia.status,
            'observacoes': anomalia.observacoes,
            'analisado_por': anomalia.analisado_por,
            'analisado_em': anomalia.analisado_em.isoformat() if anomalia.analisado_em else None,
            'created_at': anomalia.created_at.isoformat() if anomalia.created_at else None
        })
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


@router.get("/{id}", response_model=dict)
async def detalhe_anomalia(id: int, db: Session = Depends(get_db)):
    """Get anomaly details."""
    anomalia = db.query(Anomalia).filter(Anomalia.id == id).first()
    
    if not anomalia:
        raise HTTPException(status_code=404, detail="Anomalia não encontrada")
    
    return {
        'id': anomalia.id,
        'licitacao_id': anomalia.licitacao_id,
        'item_id': anomalia.item_id,
        'fornecedor_id': anomalia.fornecedor_id,
        'tipo': anomalia.tipo,
        'descricao': anomalia.descricao,
        'valor_detectado': float(anomalia.valor_detectado) if anomalia.valor_detectado else None,
        'valor_referencia': float(anomalia.valor_referencia) if anomalia.valor_referencia else None,
        'percentual_desvio': float(anomalia.percentual_desvio) if anomalia.percentual_desvio else None,
        'score_risco': float(anomalia.score_risco) if anomalia.score_risco else None,
        'status': anomalia.status,
        'observacoes': anomalia.observacoes,
        'analisado_por': anomalia.analisado_por,
        'analisado_em': anomalia.analisado_em.isoformat() if anomalia.analisado_em else None,
        'created_at': anomalia.created_at.isoformat() if anomalia.created_at else None
    }


@router.put("/{id}/status", response_model=dict)
async def atualizar_status_anomalia(
    id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db)
):
    """Update anomaly status."""
    from datetime import datetime
    
    anomalia = db.query(Anomalia).filter(Anomalia.id == id).first()
    
    if not anomalia:
        raise HTTPException(status_code=404, detail="Anomalia não encontrada")
    
    # Update fields
    anomalia.status = update.status
    
    if update.observacoes:
        anomalia.observacoes = update.observacoes
    
    if update.analisado_por:
        anomalia.analisado_por = update.analisado_por
        anomalia.analisado_em = datetime.now()
    
    db.commit()
    db.refresh(anomalia)
    
    return {
        'id': anomalia.id,
        'status': anomalia.status,
        'observacoes': anomalia.observacoes,
        'analisado_por': anomalia.analisado_por,
        'analisado_em': anomalia.analisado_em.isoformat() if anomalia.analisado_em else None
    }


@router.post("/executar-analise", response_model=dict)
async def executar_analise_anomalias(
    licitacao_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Execute anomaly analysis manually."""
    service = AnomaliaService(db)
    
    try:
        anomalias = service.executar_analise_completa(licitacao_id)
        
        return {
            'success': True,
            'total_anomalias_detectadas': len(anomalias),
            'anomalias': [
                {
                    'tipo': a.tipo,
                    'licitacao_id': a.licitacao_id,
                    'score_risco': float(a.score_risco) if a.score_risco else None
                }
                for a in anomalias
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tipos/lista", response_model=dict)
async def listar_tipos_anomalia():
    """List anomaly types."""
    return {
        'tipos': AnomaliaService.TIPOS_ANOMALIA
    }


@router.get("/estatisticas/resumo", response_model=dict)
async def estatisticas_anomalias(db: Session = Depends(get_db)):
    """Get anomaly statistics."""
    from sqlalchemy import func
    
    # Total by type
    por_tipo = db.query(
        Anomalia.tipo,
        func.count(Anomalia.id).label('total')
    ).group_by(Anomalia.tipo).all()
    
    # Total by status
    por_status = db.query(
        Anomalia.status,
        func.count(Anomalia.id).label('total')
    ).group_by(Anomalia.status).all()
    
    # Average risk score
    score_medio = db.query(func.avg(Anomalia.score_risco)).scalar()
    
    return {
        'total': db.query(Anomalia).count(),
        'por_tipo': {item.tipo: item.total for item in por_tipo},
        'por_status': {item.status: item.total for item in por_status},
        'score_risco_medio': float(score_medio) if score_medio else 0.0
    }
