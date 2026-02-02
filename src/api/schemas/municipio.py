"""API schemas for municipios."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MunicipioBase(BaseModel):
    """Base schema for municipality."""
    codigo_ibge: str
    municipio: str
    uf: str
    distancia_km: Optional[int] = None


class MunicipioResponse(MunicipioBase):
    """Response schema for municipality."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MunicipioCreate(MunicipioBase):
    """Schema for creating municipality."""
    pass
