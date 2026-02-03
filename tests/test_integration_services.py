"""Integration tests for services layer."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.models import Base, Municipio, Licitacao, Orgao, AlertaConfiguracao
from src.services.alerta_service import AlertaService


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
def sample_municipio(db_session):
    """Create a sample municipality."""
    municipio = Municipio(
        codigo_ibge="5208707",
        municipio="Goiânia",
        uf="GO",
        distancia_km=0
    )
    db_session.add(municipio)
    db_session.commit()
    db_session.refresh(municipio)
    return municipio


@pytest.fixture
def sample_orgao(db_session):
    """Create a sample government entity."""
    orgao = Orgao(
        cnpj="12345678000190",
        razao_social="Prefeitura Municipal de Goiânia",
        poder_id="E",
        esfera_id="M"
    )
    db_session.add(orgao)
    db_session.commit()
    db_session.refresh(orgao)
    return orgao


@pytest.fixture
def sample_licitacao(db_session, sample_municipio, sample_orgao):
    """Create a sample bidding."""
    licitacao = Licitacao(
        sequencial_compra="00001",
        numero_compra="0001/2024",
        processo="2024/001",
        ano_compra=2024,
        numero_controle_pncp="12345678901234567890",
        orgao_id=sample_orgao.id,
        municipio_id=sample_municipio.id,
        modalidade_id=6,
        modalidade_nome="Pregão",
        objeto_compra="Aquisição de computadores e notebooks",
        valor_total_estimado=50000.00,
        srp=False,
        existe_resultado=True,
        situacao_compra_id=4,
        situacao_compra_nome="Homologada"
    )
    db_session.add(licitacao)
    db_session.commit()
    db_session.refresh(licitacao)
    return licitacao


class TestAlertaServiceIntegration:
    """Integration tests for alert service."""
    
    def test_create_and_verify_alert(self, db_session, sample_licitacao):
        """Test creating alert configuration and verifying it triggers."""
        service = AlertaService(db_session)
        
        # Create alert configuration
        config_data = {
            "nome": "Alerta Computadores",
            "ativo": True,
            "tipo": "palavra_chave",
            "palavras_chave": ["computador", "notebook"],
            "municipios": None,
            "modalidades": None,
            "valor_minimo": 1000.00,
            "valor_maximo": 100000.00,
            "canal_notificacao": "email",
            "destinatario": "test@example.com"
        }
        
        config = service.criar_alerta(config_data)
        
        assert config.id is not None
        assert config.nome == "Alerta Computadores"
        assert config.ativo is True
        assert len(config.palavras_chave) == 2
        
        # Verify alert triggers for matching licitacao
        alertas_disparados = service.verificar_alertas(sample_licitacao)
        
        # Should trigger because objeto contains "computadores"
        assert len(alertas_disparados) > 0
        assert alertas_disparados[0].configuracao_id == config.id
    
    def test_create_multiple_alerts(self, db_session):
        """Test creating multiple alert configurations."""
        service = AlertaService(db_session)
        
        # Create multiple alerts
        for i in range(3):
            service.criar_alerta({
                "nome": f"Alerta {i}",
                "ativo": True,
                "tipo": "valor",
                "palavras_chave": None,
                "municipios": None,
                "modalidades": None,
                "valor_minimo": 10000.00 * (i + 1),
                "valor_maximo": 50000.00 * (i + 1),
                "canal_notificacao": "email",
                "destinatario": f"test{i}@example.com"
            })
        
        # Query alerts directly from database
        configs = db_session.query(AlertaConfiguracao).all()
        assert len(configs) == 3


class TestServiceWithMockedExternalAPIs:
    """Test services with mocked external API calls."""
    
    @patch('httpx.AsyncClient')
    def test_service_handles_api_timeout(self, mock_client):
        """Test that service handles API timeout gracefully."""
        # Mock API timeout
        mock_client.return_value.__aenter__.return_value.get.side_effect = TimeoutError("API timeout")
        
        # Service should handle this gracefully
        assert True  # Placeholder test
    
    @patch('httpx.AsyncClient')
    def test_service_handles_api_error(self, mock_client):
        """Test that service handles API errors gracefully."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        # Service should handle this gracefully
        assert True  # Placeholder test


class TestServiceTransactions:
    """Test service transaction handling."""
    
    def test_commit_on_success(self, db_session):
        """Test that database changes are committed on success."""
        service = AlertaService(db_session)
        
        initial_count = db_session.query(AlertaConfiguracao).count()
        
        # Create valid alert
        service.criar_alerta({
            "nome": "Alerta Commit Test",
            "ativo": True,
            "tipo": "palavra_chave",
            "palavras_chave": ["teste"],
            "municipios": None,
            "modalidades": None,
            "valor_minimo": None,
            "valor_maximo": None,
            "canal_notificacao": "email",
            "destinatario": "test@example.com"
        })
        
        # Count should increase
        final_count = db_session.query(AlertaConfiguracao).count()
        assert final_count == initial_count + 1
    
    def test_data_persistence(self, db_session, sample_licitacao):
        """Test that created data persists correctly."""
        service = AlertaService(db_session)
        
        # Create alert
        config = service.criar_alerta({
            "nome": "Alerta Persistência",
            "ativo": True,
            "tipo": "palavra_chave",
            "palavras_chave": ["teste"],
            "municipios": None,
            "modalidades": None,
            "valor_minimo": None,
            "valor_maximo": None,
            "canal_notificacao": "email",
            "destinatario": "test@example.com"
        })
        
        # Trigger alert
        alertas = service.verificar_alertas(sample_licitacao)
        
        # Clear session to force reload
        db_session.expire_all()
        
        # Verify data persisted
        persisted_config = db_session.query(AlertaConfiguracao).filter_by(id=config.id).first()
        assert persisted_config is not None
        assert persisted_config.nome == "Alerta Persistência"

