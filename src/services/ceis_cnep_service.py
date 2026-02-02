"""Service for CEIS/CNEP integration - Restricted Companies."""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models import EmpresaImpedida, Fornecedor, Resultado, Item, Licitacao


class CEISCNEPService:
    """Service for integration with CEIS/CNEP - Restricted Companies."""
    
    # URLs of the APIs (Portal da Transparência)
    CEIS_URL = "https://portaldatransparencia.gov.br/api-de-dados/ceis"
    CNEP_URL = "https://portaldatransparencia.gov.br/api-de-dados/cnep"
    
    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30
    
    async def consultar_ceis(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """Query company in CEIS (Cadastro de Empresas Inidôneas e Suspensas)."""
        try:
            # Clean CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.CEIS_URL,
                    params={'cnpjSancionado': cnpj_limpo}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data if data else None
                
        except Exception as e:
            print(f"Error querying CEIS: {e}")
        
        return None
    
    async def consultar_cnep(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """Query company in CNEP (Cadastro Nacional de Empresas Punidas)."""
        try:
            # Clean CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.CNEP_URL,
                    params={'cnpjSancionado': cnpj_limpo}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data if data else None
                
        except Exception as e:
            print(f"Error querying CNEP: {e}")
        
        return None
    
    async def verificar_impedimento(self, cnpj: str) -> Dict[str, Any]:
        """Check if company is restricted in CEIS or CNEP."""
        resultado = {
            'cnpj': cnpj,
            'impedido': False,
            'ceis': None,
            'cnep': None,
            'detalhes': []
        }
        
        # Check CEIS
        ceis_data = await self.consultar_ceis(cnpj)
        if ceis_data:
            resultado['impedido'] = True
            resultado['ceis'] = ceis_data
            resultado['detalhes'].append({
                'fonte': 'CEIS',
                'data': ceis_data
            })
        
        # Check CNEP
        cnep_data = await self.consultar_cnep(cnpj)
        if cnep_data:
            resultado['impedido'] = True
            resultado['cnep'] = cnep_data
            resultado['detalhes'].append({
                'fonte': 'CNEP',
                'data': cnep_data
            })
        
        return resultado
    
    async def atualizar_base_local(self):
        """Update local database of restricted companies."""
        # This would require downloading the full dataset
        # For now, we'll implement on-demand checking
        pass
    
    def salvar_empresa_impedida(self, dados: Dict[str, Any], fonte: str):
        """Save restricted company to local database."""
        # Extract CNPJ
        cnpj = dados.get('cnpjSancionado') or dados.get('cnpj')
        if not cnpj:
            return
        
        # Check if already exists
        existe = self.db.query(EmpresaImpedida).filter(
            and_(
                EmpresaImpedida.cnpj == cnpj,
                EmpresaImpedida.fonte == fonte
            )
        ).first()
        
        # Parse dates
        data_inicio = None
        data_fim = None
        
        if 'dataInicioSancao' in dados:
            try:
                data_inicio = datetime.strptime(dados['dataInicioSancao'], '%Y-%m-%d').date()
            except:
                pass
        
        if 'dataFimSancao' in dados:
            try:
                data_fim = datetime.strptime(dados['dataFimSancao'], '%Y-%m-%d').date()
            except:
                pass
        
        if existe:
            # Update existing
            existe.razao_social = dados.get('nomeSancionado') or dados.get('razaoSocial')
            existe.tipo_sancao = dados.get('tipoSancao')
            existe.data_inicio_sancao = data_inicio
            existe.data_fim_sancao = data_fim
            existe.orgao_sancionador = dados.get('orgaoSancionador') or dados.get('nomeOrgaoSancionador')
            existe.uf_orgao = dados.get('ufOrgaoSancionador')
            existe.fundamentacao_legal = dados.get('fundamentacaoLegal')
            existe.data_atualizacao = datetime.now()
        else:
            # Create new
            empresa = EmpresaImpedida(
                cnpj=cnpj,
                razao_social=dados.get('nomeSancionado') or dados.get('razaoSocial'),
                fonte=fonte,
                tipo_sancao=dados.get('tipoSancao'),
                data_inicio_sancao=data_inicio,
                data_fim_sancao=data_fim,
                orgao_sancionador=dados.get('orgaoSancionador') or dados.get('nomeOrgaoSancionador'),
                uf_orgao=dados.get('ufOrgaoSancionador'),
                fundamentacao_legal=dados.get('fundamentacaoLegal'),
                data_atualizacao=datetime.now()
            )
            self.db.add(empresa)
        
        self.db.commit()
    
    async def verificar_fornecedores_licitacao(self, licitacao_id: int) -> List[Dict[str, Any]]:
        """Check if any supplier in the bidding is restricted."""
        alertas = []
        
        # Get unique suppliers from this bidding
        fornecedores = self.db.query(Fornecedor).join(
            Resultado, Resultado.fornecedor_id == Fornecedor.id
        ).join(
            Item, Item.id == Resultado.item_id
        ).filter(
            Item.licitacao_id == licitacao_id
        ).distinct().all()
        
        for fornecedor in fornecedores:
            # Check in local database first
            impedimentos = self.db.query(EmpresaImpedida).filter(
                EmpresaImpedida.cnpj == fornecedor.cnpj_cpf
            ).all()
            
            # If not in local DB, check online
            if not impedimentos:
                verificacao = await self.verificar_impedimento(fornecedor.cnpj_cpf)
                
                if verificacao['impedido']:
                    # Save to local database
                    if verificacao['ceis']:
                        for item in (verificacao['ceis'] if isinstance(verificacao['ceis'], list) else [verificacao['ceis']]):
                            self.salvar_empresa_impedida(item, 'CEIS')
                    
                    if verificacao['cnep']:
                        for item in (verificacao['cnep'] if isinstance(verificacao['cnep'], list) else [verificacao['cnep']]):
                            self.salvar_empresa_impedida(item, 'CNEP')
                    
                    alertas.append({
                        'fornecedor_id': fornecedor.id,
                        'cnpj': fornecedor.cnpj_cpf,
                        'razao_social': fornecedor.razao_social,
                        'impedimentos': verificacao['detalhes']
                    })
            else:
                # Check if sanction is still active
                hoje = date.today()
                impedimentos_ativos = [
                    imp for imp in impedimentos
                    if not imp.data_fim_sancao or imp.data_fim_sancao >= hoje
                ]
                
                if impedimentos_ativos:
                    alertas.append({
                        'fornecedor_id': fornecedor.id,
                        'cnpj': fornecedor.cnpj_cpf,
                        'razao_social': fornecedor.razao_social,
                        'impedimentos': [
                            {
                                'fonte': imp.fonte,
                                'tipo_sancao': imp.tipo_sancao,
                                'data_inicio': imp.data_inicio_sancao.isoformat() if imp.data_inicio_sancao else None,
                                'data_fim': imp.data_fim_sancao.isoformat() if imp.data_fim_sancao else None,
                                'orgao': imp.orgao_sancionador
                            }
                            for imp in impedimentos_ativos
                        ]
                    })
        
        return alertas
    
    def verificar_fornecedor_local(self, cnpj: str) -> Optional[List[EmpresaImpedida]]:
        """Check if supplier is in local database of restricted companies."""
        hoje = date.today()
        
        impedimentos = self.db.query(EmpresaImpedida).filter(
            and_(
                EmpresaImpedida.cnpj == cnpj,
                or_(
                    EmpresaImpedida.data_fim_sancao.is_(None),
                    EmpresaImpedida.data_fim_sancao >= hoje
                )
            )
        ).all()
        
        return impedimentos if impedimentos else None
