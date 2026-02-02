"""Repository for municipality data access."""

from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from src.models import Municipio

logger = logging.getLogger(__name__)


class MunicipioRepository:
    """Repository for municipality operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_by_codigo_ibge(self, codigo_ibge: str) -> Optional[Municipio]:
        """Get municipality by IBGE code."""
        return self.db.query(Municipio).filter(Municipio.codigo_ibge == codigo_ibge).first()
    
    def get_all(self) -> List[Municipio]:
        """Get all municipalities."""
        return self.db.query(Municipio).all()
    
    def get_by_uf(self, uf: str) -> List[Municipio]:
        """Get municipalities by state."""
        return self.db.query(Municipio).filter(Municipio.uf == uf).all()
    
    def create(self, municipio_data: dict) -> Municipio:
        """Create new municipality."""
        municipio = Municipio(**municipio_data)
        self.db.add(municipio)
        self.db.commit()
        self.db.refresh(municipio)
        return municipio
    
    def create_bulk(self, municipios_data: List[dict]) -> int:
        """Create multiple municipalities."""
        count = 0
        for data in municipios_data:
            try:
                # Check if already exists
                existing = self.get_by_codigo_ibge(data.get("codigo_ibge"))
                if not existing:
                    self.create(data)
                    count += 1
            except Exception as e:
                logger.error(f"Error creating municipality {data.get('municipio')}: {e}")
        return count
    
    def update(self, codigo_ibge: str, municipio_data: dict) -> Optional[Municipio]:
        """Update municipality."""
        municipio = self.get_by_codigo_ibge(codigo_ibge)
        if municipio:
            for key, value in municipio_data.items():
                setattr(municipio, key, value)
            self.db.commit()
            self.db.refresh(municipio)
        return municipio
    
    def delete(self, codigo_ibge: str) -> bool:
        """Delete municipality."""
        municipio = self.get_by_codigo_ibge(codigo_ibge)
        if municipio:
            self.db.delete(municipio)
            self.db.commit()
            return True
        return False
