"""API routes for municipios."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.database.repositories import MunicipioRepository
from src.api.schemas.municipio import MunicipioResponse, MunicipioCreate

router = APIRouter()


@router.get("/", response_model=List[MunicipioResponse])
async def list_municipios(
    uf: str = Query(None, description="Filter by state"),
    db: Session = Depends(get_db)
):
    """List all municipalities."""
    repo = MunicipioRepository(db)
    if uf:
        municipios = repo.get_by_uf(uf)
    else:
        municipios = repo.get_all()
    return municipios


@router.get("/{codigo_ibge}", response_model=MunicipioResponse)
async def get_municipio(
    codigo_ibge: str,
    db: Session = Depends(get_db)
):
    """Get municipality by IBGE code."""
    repo = MunicipioRepository(db)
    municipio = repo.get_by_codigo_ibge(codigo_ibge)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio


@router.post("/", response_model=MunicipioResponse)
async def create_municipio(
    municipio: MunicipioCreate,
    db: Session = Depends(get_db)
):
    """Create new municipality."""
    repo = MunicipioRepository(db)
    # Check if already exists
    existing = repo.get_by_codigo_ibge(municipio.codigo_ibge)
    if existing:
        raise HTTPException(status_code=400, detail="Município já existe")
    
    return repo.create(municipio.model_dump())
