"""Repository for supplier data access."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from src.models import Fornecedor
from src.utils.helpers import clean_cnpj_cpf

logger = logging.getLogger(__name__)


class FornecedorRepository:
    """Repository for supplier operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_by_id(self, fornecedor_id: int) -> Optional[Fornecedor]:
        """Get supplier by ID."""
        return self.db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    
    def get_by_cnpj_cpf(self, cnpj_cpf: str) -> Optional[Fornecedor]:
        """Get supplier by CNPJ/CPF."""
        # Clean the document number
        cnpj_cpf_clean = clean_cnpj_cpf(cnpj_cpf)
        return self.db.query(Fornecedor).filter(Fornecedor.cnpj_cpf == cnpj_cpf_clean).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Fornecedor]:
        """Get all suppliers with pagination."""
        return self.db.query(Fornecedor).offset(skip).limit(limit).all()
    
    def create(self, fornecedor_data: dict) -> Fornecedor:
        """Create new supplier."""
        # Clean CNPJ/CPF
        if 'cnpj_cpf' in fornecedor_data:
            fornecedor_data['cnpj_cpf'] = clean_cnpj_cpf(fornecedor_data['cnpj_cpf'])
        
        fornecedor = Fornecedor(**fornecedor_data)
        self.db.add(fornecedor)
        self.db.commit()
        self.db.refresh(fornecedor)
        return fornecedor
    
    def get_or_create(self, cnpj_cpf: str, **kwargs) -> Fornecedor:
        """Get or create supplier."""
        cnpj_cpf_clean = clean_cnpj_cpf(cnpj_cpf)
        fornecedor = self.get_by_cnpj_cpf(cnpj_cpf_clean)
        if not fornecedor:
            fornecedor_data = {'cnpj_cpf': cnpj_cpf_clean, **kwargs}
            fornecedor = self.create(fornecedor_data)
        return fornecedor
    
    def update(self, fornecedor_id: int, fornecedor_data: dict) -> Optional[Fornecedor]:
        """Update supplier."""
        fornecedor = self.get_by_id(fornecedor_id)
        if fornecedor:
            for key, value in fornecedor_data.items():
                setattr(fornecedor, key, value)
            self.db.commit()
            self.db.refresh(fornecedor)
        return fornecedor
    
    def delete(self, fornecedor_id: int) -> bool:
        """Delete supplier."""
        fornecedor = self.get_by_id(fornecedor_id)
        if fornecedor:
            self.db.delete(fornecedor)
            self.db.commit()
            return True
        return False
    
    def search_by_name(self, name: str, limit: int = 100) -> List[Fornecedor]:
        """Search suppliers by name."""
        return self.db.query(Fornecedor).filter(
            Fornecedor.razao_social.ilike(f"%{name}%")
        ).limit(limit).all()
    
    def get_by_uf(self, uf: str) -> List[Fornecedor]:
        """Get suppliers by state."""
        return self.db.query(Fornecedor).filter(Fornecedor.uf == uf).all()
    
    def count(self) -> int:
        """Count total suppliers."""
        return self.db.query(func.count(Fornecedor.id)).scalar()
