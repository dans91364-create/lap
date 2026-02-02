"""Repository for item data access."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from src.models import Item

logger = logging.getLogger(__name__)


class ItemRepository:
    """Repository for item operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()
    
    def get_by_licitacao(self, licitacao_id: int) -> List[Item]:
        """Get all items for a bidding."""
        return self.db.query(Item).filter(Item.licitacao_id == licitacao_id).all()
    
    def create(self, item_data: dict) -> Item:
        """Create new item."""
        item = Item(**item_data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def create_bulk(self, items_data: List[dict]) -> int:
        """Create multiple items."""
        items = [Item(**data) for data in items_data]
        self.db.bulk_save_objects(items)
        self.db.commit()
        return len(items)
    
    def update(self, item_id: int, item_data: dict) -> Optional[Item]:
        """Update item."""
        item = self.get_by_id(item_id)
        if item:
            for key, value in item_data.items():
                setattr(item, key, value)
            self.db.commit()
            self.db.refresh(item)
        return item
    
    def delete(self, item_id: int) -> bool:
        """Delete item."""
        item = self.get_by_id(item_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
    
    def search_by_description(self, keyword: str, limit: int = 100) -> List[Item]:
        """Search items by description."""
        return self.db.query(Item).filter(
            Item.descricao.ilike(f"%{keyword}%")
        ).limit(limit).all()
    
    def count_by_licitacao(self, licitacao_id: int) -> int:
        """Count items for a bidding."""
        return self.db.query(func.count(Item.id)).filter(
            Item.licitacao_id == licitacao_id
        ).scalar()
