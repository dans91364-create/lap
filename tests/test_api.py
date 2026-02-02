"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api.main import app
from src.models import Municipio, Licitacao


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestMunicipiosAPI:
    """Tests for municipios API."""
    
    def test_list_municipios(self, client):
        """Test listing municipalities."""
        with patch('src.api.routes.municipios.MunicipioRepository') as mock_repo:
            mock_repo.return_value.get_all.return_value = []
            
            response = client.get("/api/v1/municipios/")
            assert response.status_code == 200
            assert isinstance(response.json(), list)


class TestLicitacoesAPI:
    """Tests for licitacoes API."""
    
    def test_list_licitacoes(self, client):
        """Test listing biddings."""
        with patch('src.api.routes.licitacoes.LicitacaoRepository') as mock_repo:
            mock_repo.return_value.get_all.return_value = []
            
            response = client.get("/api/v1/licitacoes/")
            assert response.status_code == 200
            assert isinstance(response.json(), list)
    
    def test_count_licitacoes(self, client):
        """Test counting biddings."""
        with patch('src.api.routes.licitacoes.LicitacaoRepository') as mock_repo:
            mock_repo.return_value.count.return_value = 42
            
            response = client.get("/api/v1/licitacoes/stats/count")
            assert response.status_code == 200
            assert response.json()["count"] == 42


class TestHealthEndpoints:
    """Tests for health endpoints."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert "version" in response.json()
    
    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
