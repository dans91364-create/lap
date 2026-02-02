"""API schemas for licitacoes."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LicitacaoBase(BaseModel):
    """Base schema for bidding."""
    sequencial_compra: Optional[str] = None
    numero_compra: Optional[str] = None
    processo: Optional[str] = None
    ano_compra: Optional[int] = None
    modalidade_nome: Optional[str] = None
    objeto_compra: Optional[str] = None
    valor_total_estimado: Optional[Decimal] = None
    valor_total_homologado: Optional[Decimal] = None
    data_publicacao_pncp: Optional[datetime] = None


class LicitacaoResponse(LicitacaoBase):
    """Response schema for bidding."""
    id: int
    numero_controle_pncp: Optional[str] = None
    situacao_compra_nome: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LicitacaoDetail(LicitacaoResponse):
    """Detailed schema for bidding."""
    modo_disputa_nome: Optional[str] = None
    tipo_instrumento_convocatorio_nome: Optional[str] = None
    informacao_complementar: Optional[str] = None
    srp: Optional[bool] = None
    data_abertura_proposta: Optional[datetime] = None
    data_encerramento_proposta: Optional[datetime] = None
    existe_resultado: Optional[bool] = None
    link_sistema_origem: Optional[str] = None
    
    class Config:
        from_attributes = True


class LicitacaoSearchParams(BaseModel):
    """Search parameters for bidding."""
    municipio_id: Optional[int] = Field(None, description="Municipality ID")
    modalidade_id: Optional[int] = Field(None, description="Modality ID")
    data_inicio: Optional[datetime] = Field(None, description="Start date")
    data_fim: Optional[datetime] = Field(None, description="End date")
    valor_min: Optional[float] = Field(None, description="Minimum value")
    valor_max: Optional[float] = Field(None, description="Maximum value")
    palavra_chave: Optional[str] = Field(None, description="Keyword search")
    skip: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(100, ge=1, le=100, description="Pagination limit")
