"""API routes for licitacoes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database.connection import get_db
from src.database.repositories import LicitacaoRepository
from src.api.schemas.licitacao import (
    LicitacaoResponse,
    LicitacaoDetail,
    LicitacaoSearchParams
)

router = APIRouter()


@router.get("/", response_model=List[LicitacaoResponse])
async def list_licitacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all biddings with pagination."""
    repo = LicitacaoRepository(db)
    licitacoes = repo.get_all(skip=skip, limit=limit)
    return licitacoes


@router.get("/{licitacao_id}", response_model=LicitacaoDetail)
async def get_licitacao(
    licitacao_id: int,
    db: Session = Depends(get_db)
):
    """Get bidding by ID."""
    repo = LicitacaoRepository(db)
    licitacao = repo.get_by_id(licitacao_id)
    if not licitacao:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    return licitacao


@router.get("/controle/{numero_controle}", response_model=LicitacaoDetail)
async def get_licitacao_by_controle(
    numero_controle: str,
    db: Session = Depends(get_db)
):
    """Get bidding by control number."""
    repo = LicitacaoRepository(db)
    licitacao = repo.get_by_numero_controle(numero_controle)
    if not licitacao:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    return licitacao


@router.post("/search", response_model=List[LicitacaoResponse])
async def search_licitacoes(
    params: LicitacaoSearchParams,
    db: Session = Depends(get_db)
):
    """Search biddings with filters."""
    repo = LicitacaoRepository(db)
    licitacoes = repo.search(
        municipio_id=params.municipio_id,
        modalidade_id=params.modalidade_id,
        data_inicio=params.data_inicio,
        data_fim=params.data_fim,
        valor_min=params.valor_min,
        valor_max=params.valor_max,
        palavra_chave=params.palavra_chave,
        skip=params.skip,
        limit=params.limit
    )
    return licitacoes


@router.get("/stats/count")
async def count_licitacoes(
    municipio_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Count biddings."""
    repo = LicitacaoRepository(db)
    if municipio_id:
        count = repo.count_by_municipio(municipio_id)
    else:
        count = repo.count()
    return {"count": count}
