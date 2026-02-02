"""Test configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_municipio_data():
    """Sample municipality data."""
    return {
        "codigo_ibge": "5208707",
        "municipio": "Goiânia",
        "uf": "GO",
        "distancia_km": 0
    }


@pytest.fixture
def sample_licitacao_data():
    """Sample bidding data."""
    return {
        "sequencial_compra": "00001",
        "numero_compra": "0001/2024",
        "processo": "2024/001",
        "ano_compra": 2024,
        "numero_controle_pncp": "12345678901234567890",
        "modalidade_id": 6,
        "modalidade_nome": "Pregão",
        "objeto_compra": "Aquisição de materiais de escritório",
        "valor_total_estimado": 50000.00,
        "srp": False,
        "existe_resultado": True,
        "situacao_compra_id": 4,
        "situacao_compra_nome": "Homologada"
    }
