"""Tests for database repositories."""

import pytest
from src.database.repositories import MunicipioRepository, LicitacaoRepository
from src.models import Municipio, Licitacao, Orgao


class TestMunicipioRepository:
    """Tests for municipality repository."""
    
    def test_create_municipio(self, db_session, sample_municipio_data):
        """Test creating a municipality."""
        repo = MunicipioRepository(db_session)
        municipio = repo.create(sample_municipio_data)
        
        assert municipio.id is not None
        assert municipio.codigo_ibge == "5208707"
        assert municipio.municipio == "Goiânia"
        assert municipio.uf == "GO"
    
    def test_get_by_codigo_ibge(self, db_session, sample_municipio_data):
        """Test getting municipality by IBGE code."""
        repo = MunicipioRepository(db_session)
        repo.create(sample_municipio_data)
        
        municipio = repo.get_by_codigo_ibge("5208707")
        assert municipio is not None
        assert municipio.municipio == "Goiânia"
    
    def test_get_by_uf(self, db_session, sample_municipio_data):
        """Test getting municipalities by state."""
        repo = MunicipioRepository(db_session)
        repo.create(sample_municipio_data)
        
        municipios = repo.get_by_uf("GO")
        assert len(municipios) > 0
        assert municipios[0].uf == "GO"


class TestLicitacaoRepository:
    """Tests for bidding repository."""
    
    def test_create_licitacao(self, db_session, sample_licitacao_data):
        """Test creating a bidding."""
        repo = LicitacaoRepository(db_session)
        licitacao = repo.create(sample_licitacao_data)
        
        assert licitacao.id is not None
        assert licitacao.numero_controle_pncp == "12345678901234567890"
        assert licitacao.modalidade_nome == "Pregão"
    
    def test_get_by_numero_controle(self, db_session, sample_licitacao_data):
        """Test getting bidding by control number."""
        repo = LicitacaoRepository(db_session)
        repo.create(sample_licitacao_data)
        
        licitacao = repo.get_by_numero_controle("12345678901234567890")
        assert licitacao is not None
        assert licitacao.numero_compra == "0001/2024"
    
    def test_count(self, db_session, sample_licitacao_data):
        """Test counting biddings."""
        repo = LicitacaoRepository(db_session)
        repo.create(sample_licitacao_data)
        
        count = repo.count()
        assert count == 1
