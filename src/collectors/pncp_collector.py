"""PNCP collector for bidding data."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from src.collectors.base_collector import BaseCollector
from src.utils.helpers import format_date_for_pncp, safe_get
from src.utils.constants import (
    PNCP_CONTRATACOES_ENDPOINT,
    DEFAULT_PAGE_SIZE,
    UF_GOIAS
)

logger = logging.getLogger(__name__)


class PNCPCollector(BaseCollector):
    """Collector for PNCP bidding data."""
    
    async def collect(
        self,
        data_inicial: datetime,
        data_final: datetime,
        codigo_municipio_ibge: Optional[str] = None,
        codigo_modalidade: Optional[int] = None,
        pagina: int = 1,
        tamanho_pagina: int = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        """
        Collect bidding data from PNCP API.
        
        Args:
            data_inicial: Start date
            data_final: End date
            codigo_municipio_ibge: Municipality IBGE code
            codigo_modalidade: Bidding modality code
            pagina: Page number
            tamanho_pagina: Page size
            
        Returns:
            API response with bidding data
        """
        url = f"{self.base_url}{PNCP_CONTRATACOES_ENDPOINT}"
        
        params = {
            "dataInicial": format_date_for_pncp(data_inicial),
            "dataFinal": format_date_for_pncp(data_final),
            "uf": UF_GOIAS,
            "pagina": pagina,
            "tamanhoPagina": tamanho_pagina
        }
        
        if codigo_municipio_ibge:
            params["codigoMunicipioIbge"] = codigo_municipio_ibge
            
        if codigo_modalidade:
            params["codigoModalidadeContratacao"] = codigo_modalidade
        
        try:
            response = await self._make_request(url, params=params)
            return response
        except Exception as e:
            logger.error(f"Error collecting data from PNCP: {e}")
            return {"data": [], "hasNext": False}
    
    async def collect_all_pages(
        self,
        data_inicial: datetime,
        data_final: datetime,
        codigo_municipio_ibge: Optional[str] = None,
        codigo_modalidade: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect all pages of bidding data.
        
        Args:
            data_inicial: Start date
            data_final: End date
            codigo_municipio_ibge: Municipality IBGE code
            codigo_modalidade: Bidding modality code
            
        Returns:
            List of all bidding records
        """
        all_data = []
        pagina = 1
        has_next = True
        
        while has_next:
            logger.info(f"Collecting page {pagina} for municipality {codigo_municipio_ibge or 'ALL'}")
            
            response = await self.collect(
                data_inicial=data_inicial,
                data_final=data_final,
                codigo_municipio_ibge=codigo_municipio_ibge,
                codigo_modalidade=codigo_modalidade,
                pagina=pagina
            )
            
            data = safe_get(response, "data", default=[])
            if isinstance(data, list):
                all_data.extend(data)
                logger.info(f"Collected {len(data)} records from page {pagina}")
            
            # Check if there are more pages
            has_next = safe_get(response, "hasNext", default=False)
            
            if has_next:
                pagina += 1
            else:
                logger.info(f"No more pages. Total records collected: {len(all_data)}")
        
        return all_data
    
    async def collect_by_municipality(
        self,
        municipio_ibge: str,
        years: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Collect all bidding data for a municipality.
        
        Args:
            municipio_ibge: Municipality IBGE code
            years: Number of years to go back
            
        Returns:
            List of all bidding records
        """
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=365 * years)
        
        logger.info(f"Collecting data for municipality {municipio_ibge} from {data_inicial} to {data_final}")
        
        return await self.collect_all_pages(
            data_inicial=data_inicial,
            data_final=data_final,
            codigo_municipio_ibge=municipio_ibge
        )
    
    def parse_licitacao(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse bidding data from API response.
        
        Args:
            data: Raw data from API
            
        Returns:
            Parsed bidding data
        """
        orgao = safe_get(data, "orgaoEntidade", default={})
        unidade = safe_get(data, "unidadeOrgao", default={})
        amparo = safe_get(data, "amparoLegal", default={})
        
        return {
            "sequencial_compra": safe_get(data, "sequencialCompra"),
            "numero_compra": safe_get(data, "numeroCompra"),
            "processo": safe_get(data, "processo"),
            "ano_compra": safe_get(data, "anoCompra"),
            "numero_controle_pncp": safe_get(data, "numeroControlePNCP"),
            
            # Orgão
            "orgao_cnpj": safe_get(orgao, "cnpj"),
            "orgao_razao_social": safe_get(orgao, "razaoSocial"),
            "poder_id": safe_get(orgao, "poderId"),
            "esfera_id": safe_get(orgao, "esferaId"),
            
            # Unidade
            "unidade_codigo": safe_get(unidade, "codigoUnidade"),
            "unidade_nome": safe_get(unidade, "nomeUnidade"),
            "codigo_ibge": safe_get(unidade, "codigoIbge"),
            
            # Modalidade
            "modalidade_id": safe_get(data, "modalidadeId"),
            "modalidade_nome": safe_get(data, "modalidadeNome"),
            
            # Modo Disputa
            "modo_disputa_id": safe_get(data, "modoDisputaId"),
            "modo_disputa_nome": safe_get(data, "modoDisputaNome"),
            
            # Tipo Instrumento
            "tipo_instrumento_convocatorio_nome": safe_get(data, "tipoInstrumentoConvocatorioNome"),
            
            # Amparo Legal
            "amparo_legal_descricao": safe_get(amparo, "descricao"),
            "amparo_legal_nome": safe_get(amparo, "nome"),
            "amparo_legal_codigo": safe_get(amparo, "codigo"),
            
            # Objeto
            "objeto_compra": safe_get(data, "objetoCompra"),
            "informacao_complementar": safe_get(data, "informacaoComplementar"),
            
            # SRP
            "srp": safe_get(data, "srp", default=False),
            
            # Datas
            "data_publicacao_pncp": safe_get(data, "dataPublicacaoPncp"),
            "data_abertura_proposta": safe_get(data, "dataAberturaProposta"),
            "data_encerramento_proposta": safe_get(data, "dataEncerramentoProposta"),
            "data_inclusao": safe_get(data, "dataInclusao"),
            "data_atualizacao": safe_get(data, "dataAtualizacao"),
            
            # Situação
            "situacao_compra_id": safe_get(data, "situacaoCompraId"),
            "situacao_compra_nome": safe_get(data, "situacaoCompraNome"),
            
            # Valores
            "valor_total_estimado": safe_get(data, "valorTotalEstimado"),
            "valor_total_homologado": safe_get(data, "valorTotalHomologado"),
            
            # Links e Info
            "link_sistema_origem": safe_get(data, "linkSistemaOrigem"),
            "justificativa_presencial": safe_get(data, "justificativaPresencial"),
            "existe_resultado": safe_get(data, "existeResultado", default=False),
            "orcamento_sigiloso_codigo": safe_get(data, "orcamentoSigilosoCodigo"),
            "usuario_nome": safe_get(data, "usuarioNome"),
        }
