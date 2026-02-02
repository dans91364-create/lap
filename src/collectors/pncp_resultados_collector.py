"""PNCP collector for bidding results and items."""

from typing import Dict, Any, List
import logging

from src.collectors.base_collector import BaseCollector
from src.utils.helpers import safe_get
from src.utils.constants import PNCP_ITENS_ENDPOINT, PNCP_RESULTADOS_ENDPOINT

logger = logging.getLogger(__name__)


class PNCPResultadosCollector(BaseCollector):
    """Collector for PNCP bidding items and results."""
    
    async def collect_itens(
        self,
        cnpj: str,
        ano: int,
        sequencial: str
    ) -> List[Dict[str, Any]]:
        """
        Collect items for a bidding process.
        
        Args:
            cnpj: Organization CNPJ
            ano: Year
            sequencial: Sequential number
            
        Returns:
            List of items
        """
        url = f"{self.base_url}{PNCP_ITENS_ENDPOINT.format(cnpj=cnpj, ano=ano, sequencial=sequencial)}"
        
        try:
            response = await self._make_request(url)
            # The response can be a list directly or wrapped in a dict
            if isinstance(response, list):
                return response
            return safe_get(response, "data", default=[])
        except Exception as e:
            logger.error(f"Error collecting items for {cnpj}/{ano}/{sequencial}: {e}")
            return []
    
    async def collect_resultados(
        self,
        cnpj: str,
        ano: int,
        sequencial: str,
        numero_item: int
    ) -> List[Dict[str, Any]]:
        """
        Collect results for a bidding item.
        
        Args:
            cnpj: Organization CNPJ
            ano: Year
            sequencial: Sequential number
            numero_item: Item number
            
        Returns:
            List of results
        """
        url = f"{self.base_url}{PNCP_RESULTADOS_ENDPOINT.format(cnpj=cnpj, ano=ano, sequencial=sequencial, numero_item=numero_item)}"
        
        try:
            response = await self._make_request(url)
            # The response can be a list directly or wrapped in a dict
            if isinstance(response, list):
                return response
            return safe_get(response, "data", default=[])
        except Exception as e:
            logger.error(f"Error collecting results for {cnpj}/{ano}/{sequencial}/item/{numero_item}: {e}")
            return []
    
    async def collect_all_itens_and_resultados(
        self,
        cnpj: str,
        ano: int,
        sequencial: str
    ) -> Dict[str, Any]:
        """
        Collect all items and their results for a bidding process.
        
        Args:
            cnpj: Organization CNPJ
            ano: Year
            sequencial: Sequential number
            
        Returns:
            Dictionary with items and results
        """
        itens = await self.collect_itens(cnpj, ano, sequencial)
        
        items_with_results = []
        for item in itens:
            numero_item = safe_get(item, "numeroItem")
            if numero_item:
                resultados = await self.collect_resultados(cnpj, ano, sequencial, numero_item)
                items_with_results.append({
                    "item": item,
                    "resultados": resultados
                })
            else:
                items_with_results.append({
                    "item": item,
                    "resultados": []
                })
        
        return {
            "cnpj": cnpj,
            "ano": ano,
            "sequencial": sequencial,
            "items_with_results": items_with_results
        }
    
    def parse_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse item data from API response.
        
        Args:
            data: Raw data from API
            
        Returns:
            Parsed item data
        """
        return {
            "numero_item": safe_get(data, "numeroItem"),
            "material_ou_servico": safe_get(data, "materialOuServico"),
            
            # Tipo Benefício
            "tipo_beneficio_id": safe_get(data, "tipoBeneficioId"),
            "tipo_beneficio_nome": safe_get(data, "tipoBeneficioNome"),
            
            # Incentivos
            "incentivo_produtivo_basico": safe_get(data, "incentivoProdutivoBasico", default=False),
            
            # Descrição
            "descricao": safe_get(data, "descricao"),
            "quantidade": safe_get(data, "quantidade"),
            "unidade_medida": safe_get(data, "unidadeMedida"),
            
            # Valores
            "valor_unitario_estimado": safe_get(data, "valorUnitarioEstimado"),
            "valor_total": safe_get(data, "valorTotal"),
            
            # Situação
            "situacao_compra_item_id": safe_get(data, "situacaoCompraItemId"),
            "situacao_compra_item_nome": safe_get(data, "situacaoCompraItemNome"),
            
            # Critério
            "criterio_julgamento_id": safe_get(data, "criterioJulgamentoId"),
            "criterio_julgamento_nome": safe_get(data, "criterioJulgamentoNome"),
            
            # Código e Categoria
            "codigo_produto": safe_get(data, "codigoProduto"),
            "orcamento_sigiloso": safe_get(data, "orcamentoSigiloso", default=False),
            "item_categoria_id": safe_get(data, "itemCategoriaId"),
            "item_categoria_nome": safe_get(data, "itemCategoriaNome"),
        }
    
    def parse_resultado(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse result data from API response.
        
        Args:
            data: Raw data from API
            
        Returns:
            Parsed result data
        """
        return {
            "data_resultado": safe_get(data, "dataResultado"),
            "sequencial_resultado": safe_get(data, "sequencialResultado"),
            
            # Fornecedor
            "ni_fornecedor": safe_get(data, "niFornecedor"),
            "nome_razao_social_fornecedor": safe_get(data, "nomeRazaoSocialFornecedor"),
            "tipo_pessoa": safe_get(data, "tipoPessoa"),
            "porte_fornecedor_id": safe_get(data, "porteFornecedorId"),
            "porte_fornecedor_nome": safe_get(data, "porteFornecedorNome"),
            "codigo_pais": safe_get(data, "codigoPais"),
            
            # Compra
            "numero_controle_pncp_compra": safe_get(data, "numeroControlePNCPCompra"),
            "indicador_subcontratacao": safe_get(data, "indicadorSubcontratacao", default=False),
            
            # Valores
            "percentual_desconto": safe_get(data, "percentualDesconto"),
            "quantidade_homologada": safe_get(data, "quantidadeHomologada"),
            "valor_unitario_homologado": safe_get(data, "valorUnitarioHomologado"),
            "valor_total_homologado": safe_get(data, "valorTotalHomologado"),
            
            # Situação
            "situacao_compra_item_resultado_id": safe_get(data, "situacaoCompraItemResultadoId"),
            
            # Datas
            "data_inclusao": safe_get(data, "dataInclusao"),
            "data_atualizacao": safe_get(data, "dataAtualizacao"),
        }
