"""API routes for intelligent alerts."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.connection import get_db
from src.models import AlertaConfiguracao, AlertaDisparado
from src.services.alerta_service import AlertaService


router = APIRouter(prefix="/api/v1/alertas", tags=["Alertas"])


class AlertaConfigSchema(BaseModel):
    nome: str
    ativo: bool = True
    tipo: str
    palavras_chave: Optional[List[str]] = None
    municipios: Optional[List[int]] = None
    modalidades: Optional[List[str]] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    canal_notificacao: str
    destinatario: str


@router.get("/configuracoes", response_model=dict)
async def listar_configuracoes_alerta(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List alert configurations."""
    # Build query
    query = db.query(AlertaConfiguracao)
    
    # Count total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    configs = query.order_by(AlertaConfiguracao.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Convert to dict
    items = []
    for config in configs:
        items.append({
            'id': config.id,
            'nome': config.nome,
            'ativo': config.ativo,
            'tipo': config.tipo,
            'palavras_chave': config.palavras_chave,
            'municipios': config.municipios,
            'modalidades': config.modalidades,
            'valor_minimo': float(config.valor_minimo) if config.valor_minimo else None,
            'valor_maximo': float(config.valor_maximo) if config.valor_maximo else None,
            'canal_notificacao': config.canal_notificacao,
            'destinatario': config.destinatario,
            'created_at': config.created_at.isoformat() if config.created_at else None
        })
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


@router.post("/configuracoes", response_model=dict)
async def criar_configuracao_alerta(
    config: AlertaConfigSchema,
    db: Session = Depends(get_db)
):
    """Create new alert configuration."""
    service = AlertaService(db)
    
    try:
        nova_config = service.criar_alerta(config.dict())
        
        return {
            'id': nova_config.id,
            'nome': nova_config.nome,
            'ativo': nova_config.ativo,
            'tipo': nova_config.tipo,
            'created_at': nova_config.created_at.isoformat() if nova_config.created_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuracoes/{id}", response_model=dict)
async def detalhe_configuracao_alerta(id: int, db: Session = Depends(get_db)):
    """Get alert configuration details."""
    config = db.query(AlertaConfiguracao).filter(AlertaConfiguracao.id == id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    return {
        'id': config.id,
        'nome': config.nome,
        'ativo': config.ativo,
        'tipo': config.tipo,
        'palavras_chave': config.palavras_chave,
        'municipios': config.municipios,
        'modalidades': config.modalidades,
        'valor_minimo': float(config.valor_minimo) if config.valor_minimo else None,
        'valor_maximo': float(config.valor_maximo) if config.valor_maximo else None,
        'canal_notificacao': config.canal_notificacao,
        'destinatario': config.destinatario,
        'created_at': config.created_at.isoformat() if config.created_at else None
    }


@router.put("/configuracoes/{id}", response_model=dict)
async def atualizar_configuracao_alerta(
    id: int,
    config: AlertaConfigSchema,
    db: Session = Depends(get_db)
):
    """Update alert configuration."""
    from datetime import datetime
    
    config_db = db.query(AlertaConfiguracao).filter(AlertaConfiguracao.id == id).first()
    
    if not config_db:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Update fields
    config_db.nome = config.nome
    config_db.ativo = config.ativo
    config_db.tipo = config.tipo
    config_db.palavras_chave = config.palavras_chave
    config_db.municipios = config.municipios
    config_db.modalidades = config.modalidades
    config_db.valor_minimo = config.valor_minimo
    config_db.valor_maximo = config.valor_maximo
    config_db.canal_notificacao = config.canal_notificacao
    config_db.destinatario = config.destinatario
    config_db.updated_at = datetime.now()
    
    db.commit()
    db.refresh(config_db)
    
    return {
        'id': config_db.id,
        'nome': config_db.nome,
        'ativo': config_db.ativo
    }


@router.delete("/configuracoes/{id}", response_model=dict)
async def deletar_configuracao_alerta(id: int, db: Session = Depends(get_db)):
    """Delete alert configuration."""
    config = db.query(AlertaConfiguracao).filter(AlertaConfiguracao.id == id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    db.delete(config)
    db.commit()
    
    return {'success': True}


@router.get("/disparados", response_model=dict)
async def listar_alertas_disparados(
    enviado: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List triggered alerts."""
    # Build query
    query = db.query(AlertaDisparado)
    
    if enviado is not None:
        query = query.filter(AlertaDisparado.enviado == enviado)
    
    # Count total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    alertas = query.order_by(AlertaDisparado.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Convert to dict
    items = []
    for alerta in alertas:
        items.append({
            'id': alerta.id,
            'configuracao_id': alerta.configuracao_id,
            'licitacao_id': alerta.licitacao_id,
            'mensagem': alerta.mensagem,
            'enviado': alerta.enviado,
            'enviado_em': alerta.enviado_em.isoformat() if alerta.enviado_em else None,
            'erro': alerta.erro,
            'created_at': alerta.created_at.isoformat() if alerta.created_at else None
        })
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


@router.post("/disparados/{id}/reenviar", response_model=dict)
async def reenviar_alerta(id: int, db: Session = Depends(get_db)):
    """Resend alert."""
    alerta = db.query(AlertaDisparado).filter(AlertaDisparado.id == id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    
    service = AlertaService(db)
    config = alerta.configuracao
    
    success = False
    if config.canal_notificacao == 'email':
        success = service.enviar_notificacao_email(alerta)
    elif config.canal_notificacao == 'telegram':
        success = service.enviar_notificacao_telegram(alerta)
    
    return {
        'success': success,
        'enviado': alerta.enviado,
        'enviado_em': alerta.enviado_em.isoformat() if alerta.enviado_em else None
    }


@router.get("/estatisticas", response_model=dict)
async def estatisticas_alertas(db: Session = Depends(get_db)):
    """Get alert statistics."""
    from sqlalchemy import func
    
    # Total configurations
    total_configs = db.query(AlertaConfiguracao).count()
    configs_ativas = db.query(AlertaConfiguracao).filter(AlertaConfiguracao.ativo == True).count()
    
    # Total triggered
    total_disparados = db.query(AlertaDisparado).count()
    enviados = db.query(AlertaDisparado).filter(AlertaDisparado.enviado == True).count()
    pendentes = db.query(AlertaDisparado).filter(AlertaDisparado.enviado == False).count()
    
    # By channel
    por_canal = db.query(
        AlertaConfiguracao.canal_notificacao,
        func.count(AlertaConfiguracao.id).label('total')
    ).group_by(AlertaConfiguracao.canal_notificacao).all()
    
    return {
        'configuracoes': {
            'total': total_configs,
            'ativas': configs_ativas,
            'inativas': total_configs - configs_ativas
        },
        'disparados': {
            'total': total_disparados,
            'enviados': enviados,
            'pendentes': pendentes
        },
        'por_canal': {item.canal_notificacao: item.total for item in por_canal}
    }
