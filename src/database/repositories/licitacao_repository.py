"""Repository for bidding data access."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import logging

from src.models import Licitacao, Orgao, Municipio
from src.utils.helpers import parse_pncp_datetime

logger = logging.getLogger(__name__)


class LicitacaoRepository:
    """Repository for bidding operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_by_id(self, licitacao_id: int) -> Optional[Licitacao]:
        """Get bidding by ID."""
        return self.db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()
    
    def get_by_numero_controle(self, numero_controle: str) -> Optional[Licitacao]:
        """Get bidding by control number."""
        return self.db.query(Licitacao).filter(Licitacao.numero_controle_pncp == numero_controle).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Licitacao]:
        """Get all biddings with pagination."""
        return self.db.query(Licitacao).offset(skip).limit(limit).all()
    
    def create(self, licitacao_data: dict) -> Licitacao:
        """Create new bidding."""
        # Parse datetime fields
        datetime_fields = [
            'data_publicacao_pncp', 'data_abertura_proposta', 
            'data_encerramento_proposta', 'data_inclusao', 'data_atualizacao'
        ]
        for field in datetime_fields:
            if field in licitacao_data and licitacao_data[field]:
                licitacao_data[field] = parse_pncp_datetime(licitacao_data[field])
        
        licitacao = Licitacao(**licitacao_data)
        self.db.add(licitacao)
        self.db.commit()
        self.db.refresh(licitacao)
        return licitacao
    
    def update(self, licitacao_id: int, licitacao_data: dict) -> Optional[Licitacao]:
        """Update bidding."""
        licitacao = self.get_by_id(licitacao_id)
        if licitacao:
            for key, value in licitacao_data.items():
                setattr(licitacao, key, value)
            self.db.commit()
            self.db.refresh(licitacao)
        return licitacao
    
    def delete(self, licitacao_id: int) -> bool:
        """Delete bidding."""
        licitacao = self.get_by_id(licitacao_id)
        if licitacao:
            self.db.delete(licitacao)
            self.db.commit()
            return True
        return False
    
    def search(
        self,
        municipio_id: Optional[int] = None,
        modalidade_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None,
        palavra_chave: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Licitacao]:
        """Search biddings with filters."""
        query = self.db.query(Licitacao)
        
        if municipio_id:
            query = query.filter(Licitacao.municipio_id == municipio_id)
        
        if modalidade_id:
            query = query.filter(Licitacao.modalidade_id == modalidade_id)
        
        if data_inicio:
            query = query.filter(Licitacao.data_publicacao_pncp >= data_inicio)
        
        if data_fim:
            query = query.filter(Licitacao.data_publicacao_pncp <= data_fim)
        
        if valor_min:
            query = query.filter(Licitacao.valor_total_estimado >= valor_min)
        
        if valor_max:
            query = query.filter(Licitacao.valor_total_estimado <= valor_max)
        
        if palavra_chave:
            query = query.filter(
                or_(
                    Licitacao.objeto_compra.ilike(f"%{palavra_chave}%"),
                    Licitacao.informacao_complementar.ilike(f"%{palavra_chave}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_or_create_orgao(self, cnpj: str, razao_social: str, **kwargs) -> Orgao:
        """Get or create organization."""
        orgao = self.db.query(Orgao).filter(Orgao.cnpj == cnpj).first()
        if not orgao:
            orgao = Orgao(cnpj=cnpj, razao_social=razao_social, **kwargs)
            self.db.add(orgao)
            self.db.commit()
            self.db.refresh(orgao)
        return orgao
    
    def count(self) -> int:
        """Count total biddings."""
        return self.db.query(func.count(Licitacao.id)).scalar()
    
    def count_by_municipio(self, municipio_id: int) -> int:
        """Count biddings by municipality."""
        return self.db.query(func.count(Licitacao.id)).filter(
            Licitacao.municipio_id == municipio_id
        ).scalar()
