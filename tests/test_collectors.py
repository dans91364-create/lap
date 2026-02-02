"""Tests for collectors."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.collectors.pncp_collector import PNCPCollector
from src.collectors.pncp_resultados_collector import PNCPResultadosCollector


class TestPNCPCollector:
    """Tests for PNCP collector."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        return PNCPCollector()
    
    def test_parse_licitacao(self, collector):
        """Test parsing of bidding data."""
        raw_data = {
            "sequencialCompra": "00001",
            "numeroCompra": "0001/2024",
            "anoCompra": 2024,
            "numeroControlePNCP": "12345678901234567890",
            "orgaoEntidade": {
                "cnpj": "12345678000190",
                "razaoSocial": "Prefeitura Municipal",
                "poderId": "E",
                "esferaId": "M"
            },
            "unidadeOrgao": {
                "codigoUnidade": "001",
                "nomeUnidade": "Secretaria de Administração",
                "codigoIbge": "5208707"
            },
            "modalidadeId": 6,
            "modalidadeNome": "Pregão",
            "objetoCompra": "Aquisição de materiais",
            "valorTotalEstimado": 50000.00,
            "srp": False,
            "existeResultado": True
        }
        
        parsed = collector.parse_licitacao(raw_data)
        
        assert parsed["sequencial_compra"] == "00001"
        assert parsed["numero_compra"] == "0001/2024"
        assert parsed["ano_compra"] == 2024
        assert parsed["orgao_cnpj"] == "12345678000190"
        assert parsed["modalidade_id"] == 6
        assert parsed["objeto_compra"] == "Aquisição de materiais"


class TestPNCPResultadosCollector:
    """Tests for PNCP results collector."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        return PNCPResultadosCollector()
    
    def test_parse_item(self, collector):
        """Test parsing of item data."""
        raw_data = {
            "numeroItem": 1,
            "materialOuServico": "M",
            "descricao": "Papel A4",
            "quantidade": 100,
            "unidadeMedida": "Resma",
            "valorUnitarioEstimado": 25.00,
            "valorTotal": 2500.00
        }
        
        parsed = collector.parse_item(raw_data)
        
        assert parsed["numero_item"] == 1
        assert parsed["material_ou_servico"] == "M"
        assert parsed["descricao"] == "Papel A4"
        assert parsed["quantidade"] == 100
        assert parsed["valor_total"] == 2500.00
    
    def test_parse_resultado(self, collector):
        """Test parsing of result data."""
        raw_data = {
            "niFornecedor": "12345678000190",
            "nomeRazaoSocialFornecedor": "Fornecedor XYZ Ltda",
            "quantidadeHomologada": 100,
            "valorUnitarioHomologado": 24.00,
            "valorTotalHomologado": 2400.00,
            "percentualDesconto": 4.00
        }
        
        parsed = collector.parse_resultado(raw_data)
        
        assert parsed["ni_fornecedor"] == "12345678000190"
        assert parsed["nome_razao_social_fornecedor"] == "Fornecedor XYZ Ltda"
        assert parsed["quantidade_homologada"] == 100
        assert parsed["valor_total_homologado"] == 2400.00
