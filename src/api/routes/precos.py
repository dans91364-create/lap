"""API routes for price analysis."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.services.analise_precos_service import AnalisePrecoService


router = APIRouter(prefix="/api/v1/precos", tags=["Preços"])


@router.get("/historico", response_model=dict)
async def historico_precos(
    descricao: str = Query(..., description="Item description"),
    periodo_meses: int = Query(24, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get price history for an item."""
    service = AnalisePrecoService(db)
    
    try:
        timeline = service.historico_precos_timeline(descricao, periodo_meses)
        
        return {
            'descricao': descricao,
            'periodo_meses': periodo_meses,
            'total_registros': len(timeline),
            'historico': timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estatisticas", response_model=dict)
async def estatisticas_precos(
    descricao: str = Query(..., description="Item description"),
    periodo_meses: int = Query(24, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get price statistics for an item."""
    service = AnalisePrecoService(db)
    
    try:
        stats = service.calcular_estatisticas_item(descricao, periodo_meses)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark", response_model=dict)
async def benchmark_precos(
    descricao: str = Query(..., description="Item description"),
    db: Session = Depends(get_db)
):
    """Get regional price benchmark."""
    service = AnalisePrecoService(db)
    
    try:
        benchmark = service.benchmark_regional(descricao)
        
        return benchmark
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sugestao", response_model=dict)
async def sugestao_preco(
    descricao: str = Query(..., description="Item description"),
    db: Session = Depends(get_db)
):
    """Suggest reference price."""
    service = AnalisePrecoService(db)
    
    try:
        sugestao = service.sugerir_preco_referencia(descricao)
        
        return sugestao
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outliers", response_model=dict)
async def detectar_outliers(
    descricao: str = Query(..., description="Item description"),
    db: Session = Depends(get_db)
):
    """Detect price outliers."""
    service = AnalisePrecoService(db)
    
    try:
        outliers = service.detectar_outliers(descricao)
        
        return {
            'descricao': descricao,
            'total_outliers': len(outliers),
            'outliers': outliers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tendencia", response_model=dict)
async def analisar_tendencia(
    descricao: str = Query(..., description="Item description"),
    periodo_meses: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Analyze price trend."""
    service = AnalisePrecoService(db)
    
    try:
        tendencia = service.analisar_tendencia(descricao, periodo_meses)
        
        return tendencia
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{item_id}/comparar", response_model=dict)
async def comparar_preco_item(item_id: int, db: Session = Depends(get_db)):
    """Compare item price with historical data."""
    service = AnalisePrecoService(db)
    
    try:
        comparacao = service.comparar_preco_historico(item_id)
        
        return comparacao
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
