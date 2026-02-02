"""Collection service for gathering bidding data."""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.collectors import PNCPCollector, PNCPResultadosCollector
from src.database.connection import get_db_context
from src.database.repositories import (
    MunicipioRepository,
    LicitacaoRepository,
    ItemRepository,
    FornecedorRepository
)
from src.utils.helpers import get_date_range, clean_cnpj_cpf
from src.models import Resultado

logger = logging.getLogger(__name__)


class ColetaService:
    """Service for collecting bidding data."""
    
    def __init__(self):
        """Initialize collection service."""
        self.pncp_collector = PNCPCollector()
        self.resultados_collector = PNCPResultadosCollector()
    
    async def load_municipios_from_config(self):
        """Load municipalities from configuration file."""
        try:
            with open('config/municipios_200km.json', 'r', encoding='utf-8') as f:
                municipios_data = json.load(f)
            
            with get_db_context() as db:
                repo = MunicipioRepository(db)
                count = repo.create_bulk(municipios_data)
                logger.info(f"Loaded {count} municipalities from config")
                return count
        except Exception as e:
            logger.error(f"Error loading municipalities: {e}")
            raise
    
    async def collect_licitacoes_for_municipio(
        self,
        codigo_ibge: str,
        years: int = 2
    ) -> int:
        """
        Collect biddings for a municipality.
        
        Args:
            codigo_ibge: Municipality IBGE code
            years: Number of years to collect
            
        Returns:
            Number of biddings collected
        """
        logger.info(f"Starting collection for municipality {codigo_ibge}")
        
        # Collect data from PNCP
        licitacoes_data = await self.pncp_collector.collect_by_municipality(
            codigo_ibge, years
        )
        
        count = 0
        with get_db_context() as db:
            municipio_repo = MunicipioRepository(db)
            licitacao_repo = LicitacaoRepository(db)
            
            # Get municipality
            municipio = municipio_repo.get_by_codigo_ibge(codigo_ibge)
            if not municipio:
                logger.warning(f"Municipality {codigo_ibge} not found in database")
                return 0
            
            for licitacao_raw in licitacoes_data:
                try:
                    # Parse licitacao data
                    parsed = self.pncp_collector.parse_licitacao(licitacao_raw)
                    
                    # Check if already exists
                    numero_controle = parsed.get('numero_controle_pncp')
                    if numero_controle and licitacao_repo.get_by_numero_controle(numero_controle):
                        logger.debug(f"Licitação {numero_controle} already exists, skipping")
                        continue
                    
                    # Get or create orgao
                    orgao = licitacao_repo.get_or_create_orgao(
                        cnpj=parsed.get('orgao_cnpj'),
                        razao_social=parsed.get('orgao_razao_social', 'N/A'),
                        poder_id=parsed.get('poder_id'),
                        esfera_id=parsed.get('esfera_id')
                    )
                    
                    # Create licitacao
                    licitacao_data = {
                        'sequencial_compra': parsed.get('sequencial_compra'),
                        'numero_compra': parsed.get('numero_compra'),
                        'processo': parsed.get('processo'),
                        'ano_compra': parsed.get('ano_compra'),
                        'numero_controle_pncp': numero_controle,
                        'orgao_id': orgao.id,
                        'municipio_id': municipio.id,
                        'modalidade_id': parsed.get('modalidade_id'),
                        'modalidade_nome': parsed.get('modalidade_nome'),
                        'modo_disputa_id': parsed.get('modo_disputa_id'),
                        'modo_disputa_nome': parsed.get('modo_disputa_nome'),
                        'tipo_instrumento_convocatorio_nome': parsed.get('tipo_instrumento_convocatorio_nome'),
                        'amparo_legal_descricao': parsed.get('amparo_legal_descricao'),
                        'amparo_legal_nome': parsed.get('amparo_legal_nome'),
                        'amparo_legal_codigo': parsed.get('amparo_legal_codigo'),
                        'objeto_compra': parsed.get('objeto_compra'),
                        'informacao_complementar': parsed.get('informacao_complementar'),
                        'srp': parsed.get('srp'),
                        'data_publicacao_pncp': parsed.get('data_publicacao_pncp'),
                        'data_abertura_proposta': parsed.get('data_abertura_proposta'),
                        'data_encerramento_proposta': parsed.get('data_encerramento_proposta'),
                        'data_inclusao': parsed.get('data_inclusao'),
                        'data_atualizacao': parsed.get('data_atualizacao'),
                        'situacao_compra_id': parsed.get('situacao_compra_id'),
                        'situacao_compra_nome': parsed.get('situacao_compra_nome'),
                        'valor_total_estimado': parsed.get('valor_total_estimado'),
                        'valor_total_homologado': parsed.get('valor_total_homologado'),
                        'link_sistema_origem': parsed.get('link_sistema_origem'),
                        'justificativa_presencial': parsed.get('justificativa_presencial'),
                        'existe_resultado': parsed.get('existe_resultado'),
                        'orcamento_sigiloso_codigo': parsed.get('orcamento_sigiloso_codigo'),
                        'usuario_nome': parsed.get('usuario_nome'),
                        'unidade_codigo': parsed.get('unidade_codigo'),
                        'unidade_nome': parsed.get('unidade_nome'),
                    }
                    
                    licitacao_repo.create(licitacao_data)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing licitacao: {e}")
                    continue
        
        logger.info(f"Collected {count} biddings for municipality {codigo_ibge}")
        return count
    
    async def collect_all_municipios(self, years: int = 2) -> Dict[str, int]:
        """
        Collect biddings for all municipalities.
        
        Args:
            years: Number of years to collect
            
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            'total_municipios': 0,
            'total_licitacoes': 0,
            'errors': 0
        }
        
        with get_db_context() as db:
            repo = MunicipioRepository(db)
            municipios = repo.get_all()
            stats['total_municipios'] = len(municipios)
        
        for municipio in municipios:
            try:
                count = await self.collect_licitacoes_for_municipio(
                    municipio.codigo_ibge, years
                )
                stats['total_licitacoes'] += count
            except Exception as e:
                logger.error(f"Error collecting for {municipio.municipio}: {e}")
                stats['errors'] += 1
        
        return stats
    
    async def collect_itens_and_resultados(
        self,
        licitacao_id: int
    ) -> Dict[str, int]:
        """
        Collect items and results for a bidding.
        
        Args:
            licitacao_id: Bidding ID
            
        Returns:
            Dictionary with collection statistics
        """
        stats = {'itens': 0, 'resultados': 0}
        
        with get_db_context() as db:
            licitacao_repo = LicitacaoRepository(db)
            item_repo = ItemRepository(db)
            fornecedor_repo = FornecedorRepository(db)
            
            licitacao = licitacao_repo.get_by_id(licitacao_id)
            if not licitacao:
                logger.error(f"Licitação {licitacao_id} not found")
                return stats
            
            # Get orgao CNPJ
            if not licitacao.orgao or not licitacao.orgao.cnpj:
                logger.error(f"Orgao CNPJ not found for licitacao {licitacao_id}")
                return stats
            
            cnpj = clean_cnpj_cpf(licitacao.orgao.cnpj)
            ano = licitacao.ano_compra
            sequencial = licitacao.sequencial_compra
            
            if not all([cnpj, ano, sequencial]):
                logger.error(f"Missing required data for licitacao {licitacao_id}")
                return stats
            
            # Collect items and results
            data = await self.resultados_collector.collect_all_itens_and_resultados(
                cnpj, ano, sequencial
            )
            
            for item_data in data.get('items_with_results', []):
                try:
                    # Parse and create item
                    item_parsed = self.resultados_collector.parse_item(item_data['item'])
                    item_parsed['licitacao_id'] = licitacao_id
                    
                    item = item_repo.create(item_parsed)
                    stats['itens'] += 1
                    
                    # Process results
                    for resultado_raw in item_data.get('resultados', []):
                        try:
                            resultado_parsed = self.resultados_collector.parse_resultado(resultado_raw)
                            
                            # Get or create fornecedor
                            fornecedor = fornecedor_repo.get_or_create(
                                cnpj_cpf=resultado_parsed['ni_fornecedor'],
                                razao_social=resultado_parsed['nome_razao_social_fornecedor'],
                                tipo_pessoa=resultado_parsed.get('tipo_pessoa'),
                                porte_fornecedor_id=resultado_parsed.get('porte_fornecedor_id'),
                                porte_fornecedor_nome=resultado_parsed.get('porte_fornecedor_nome'),
                                codigo_pais=resultado_parsed.get('codigo_pais')
                            )
                            
                            # Create resultado
                            resultado = Resultado(
                                item_id=item.id,
                                fornecedor_id=fornecedor.id,
                                data_resultado=resultado_parsed.get('data_resultado'),
                                sequencial_resultado=resultado_parsed.get('sequencial_resultado'),
                                numero_controle_pncp_compra=resultado_parsed.get('numero_controle_pncp_compra'),
                                indicador_subcontratacao=resultado_parsed.get('indicador_subcontratacao'),
                                percentual_desconto=resultado_parsed.get('percentual_desconto'),
                                quantidade_homologada=resultado_parsed.get('quantidade_homologada'),
                                valor_unitario_homologado=resultado_parsed.get('valor_unitario_homologado'),
                                valor_total_homologado=resultado_parsed.get('valor_total_homologado'),
                                situacao_compra_item_resultado_id=resultado_parsed.get('situacao_compra_item_resultado_id'),
                                data_inclusao=resultado_parsed.get('data_inclusao'),
                                data_atualizacao=resultado_parsed.get('data_atualizacao')
                            )
                            db.add(resultado)
                            db.commit()
                            stats['resultados'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing resultado: {e}")
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    continue
        
        logger.info(f"Collected {stats['itens']} items and {stats['resultados']} results for licitacao {licitacao_id}")
        return stats
