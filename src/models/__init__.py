"""Database models for the LAP system."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Municipio(Base):
    """Model for municipalities."""
    __tablename__ = "municipios"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String(7), unique=True, nullable=False, index=True)
    municipio = Column(String(100), nullable=False)
    uf = Column(String(2), nullable=False)
    distancia_km = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licitacoes = relationship("Licitacao", back_populates="municipio")


class Orgao(Base):
    """Model for government entities."""
    __tablename__ = "orgaos"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    poder_id = Column(String(20))
    esfera_id = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licitacoes = relationship("Licitacao", back_populates="orgao")


class Licitacao(Base):
    """Model for bidding processes."""
    __tablename__ = "licitacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    sequencial_compra = Column(String(20))
    numero_compra = Column(String(50))
    processo = Column(String(50))
    ano_compra = Column(Integer)
    numero_controle_pncp = Column(String(100), unique=True, index=True)
    
    # Foreign Keys
    orgao_id = Column(Integer, ForeignKey("orgaos.id"))
    municipio_id = Column(Integer, ForeignKey("municipios.id"))
    
    # Modalidade
    modalidade_id = Column(Integer)
    modalidade_nome = Column(String(100))
    
    # Modo de Disputa
    modo_disputa_id = Column(Integer)
    modo_disputa_nome = Column(String(100))
    
    # Tipo Instrumento
    tipo_instrumento_convocatorio_nome = Column(String(100))
    
    # Amparo Legal
    amparo_legal_descricao = Column(Text)
    amparo_legal_nome = Column(String(255))
    amparo_legal_codigo = Column(String(50))
    
    # Objeto
    objeto_compra = Column(Text)
    informacao_complementar = Column(Text)
    
    # Sistema de Registro de Preços
    srp = Column(Boolean, default=False)
    
    # Datas
    data_publicacao_pncp = Column(DateTime)
    data_abertura_proposta = Column(DateTime)
    data_encerramento_proposta = Column(DateTime)
    data_inclusao = Column(DateTime)
    data_atualizacao = Column(DateTime)
    
    # Situação
    situacao_compra_id = Column(Integer)
    situacao_compra_nome = Column(String(100))
    
    # Valores
    valor_total_estimado = Column(Numeric(15, 2))
    valor_total_homologado = Column(Numeric(15, 2))
    
    # Links e Informações Adicionais
    link_sistema_origem = Column(Text)
    justificativa_presencial = Column(Text)
    existe_resultado = Column(Boolean, default=False)
    orcamento_sigiloso_codigo = Column(String(10))
    usuario_nome = Column(String(255))
    
    # Unidade Orgão
    unidade_codigo = Column(String(20))
    unidade_nome = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orgao = relationship("Orgao", back_populates="licitacoes")
    municipio = relationship("Municipio", back_populates="licitacoes")
    itens = relationship("Item", back_populates="licitacao", cascade="all, delete-orphan")


class Item(Base):
    """Model for bidding items."""
    __tablename__ = "itens"
    
    id = Column(Integer, primary_key=True, index=True)
    licitacao_id = Column(Integer, ForeignKey("licitacoes.id"), nullable=False)
    
    numero_item = Column(Integer, nullable=False)
    material_ou_servico = Column(String(1))  # M = Material, S = Serviço
    
    # Tipo Benefício
    tipo_beneficio_id = Column(Integer)
    tipo_beneficio_nome = Column(String(100))
    
    # Incentivos
    incentivo_produtivo_basico = Column(Boolean, default=False)
    
    # Descrição e Quantidade
    descricao = Column(Text, nullable=False)
    quantidade = Column(Numeric(15, 4))
    unidade_medida = Column(String(50))
    
    # Valores
    valor_unitario_estimado = Column(Numeric(15, 2))
    valor_total = Column(Numeric(15, 2))
    
    # Situação
    situacao_compra_item_id = Column(Integer)
    situacao_compra_item_nome = Column(String(100))
    
    # Critério de Julgamento
    criterio_julgamento_id = Column(Integer)
    criterio_julgamento_nome = Column(String(100))
    
    # Código e Categoria
    codigo_produto = Column(String(50))
    orcamento_sigiloso = Column(Boolean, default=False)
    item_categoria_id = Column(Integer)
    item_categoria_nome = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licitacao = relationship("Licitacao", back_populates="itens")
    resultados = relationship("Resultado", back_populates="item", cascade="all, delete-orphan")


class Fornecedor(Base):
    """Model for suppliers."""
    __tablename__ = "fornecedores"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj_cpf = Column(String(14), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    
    # Porte
    porte_fornecedor_id = Column(Integer)
    porte_fornecedor_nome = Column(String(50))  # ME, EPP, DEMAIS
    
    # Tipo Pessoa
    tipo_pessoa = Column(String(2))  # PJ, PF
    
    # Localização
    municipio = Column(String(100))
    uf = Column(String(2))
    codigo_pais = Column(String(10))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resultados = relationship("Resultado", back_populates="fornecedor")


class Resultado(Base):
    """Model for bidding results."""
    __tablename__ = "resultados"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("itens.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    
    # Data e Sequencial
    data_resultado = Column(Date)
    sequencial_resultado = Column(Integer)
    
    # Informações Adicionais
    numero_controle_pncp_compra = Column(String(100))
    indicador_subcontratacao = Column(Boolean, default=False)
    
    # Valores
    percentual_desconto = Column(Numeric(5, 2))
    quantidade_homologada = Column(Numeric(15, 4))
    valor_unitario_homologado = Column(Numeric(15, 2))
    valor_total_homologado = Column(Numeric(15, 2))
    
    # Situação
    situacao_compra_item_resultado_id = Column(Integer)
    
    # Metadata
    data_inclusao = Column(DateTime)
    data_atualizacao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="resultados")
    fornecedor = relationship("Fornecedor", back_populates="resultados")


class Anomalia(Base):
    """Model for detected anomalies in biddings."""
    __tablename__ = "anomalias"
    
    id = Column(Integer, primary_key=True, index=True)
    licitacao_id = Column(Integer, ForeignKey("licitacoes.id"))
    item_id = Column(Integer)
    fornecedor_id = Column(Integer)
    tipo = Column(String(50), nullable=False, index=True)
    descricao = Column(Text)
    valor_detectado = Column(Numeric(15, 2))
    valor_referencia = Column(Numeric(15, 2))
    percentual_desvio = Column(Numeric(10, 2))
    score_risco = Column(Numeric(5, 2))
    status = Column(String(20), default='pendente', index=True)
    observacoes = Column(Text)
    analisado_por = Column(String(100))
    analisado_em = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AlertaConfiguracao(Base):
    """Model for alert configurations."""
    __tablename__ = "alertas_configuracao"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    palavras_chave = Column(JSON, nullable=True)
    municipios = Column(JSON, nullable=True)
    modalidades = Column(JSON, nullable=True)
    valor_minimo = Column(Numeric(15, 2))
    valor_maximo = Column(Numeric(15, 2))
    canal_notificacao = Column(String(20), nullable=False)
    destinatario = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    disparados = relationship("AlertaDisparado", back_populates="configuracao", cascade="all, delete-orphan")


class AlertaDisparado(Base):
    """Model for triggered alerts."""
    __tablename__ = "alertas_disparados"
    
    id = Column(Integer, primary_key=True, index=True)
    configuracao_id = Column(Integer, ForeignKey("alertas_configuracao.id"), nullable=False, index=True)
    licitacao_id = Column(Integer, ForeignKey("licitacoes.id"), index=True)
    mensagem = Column(Text)
    enviado = Column(Boolean, default=False, index=True)
    enviado_em = Column(DateTime)
    erro = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    configuracao = relationship("AlertaConfiguracao", back_populates="disparados")


class EmpresaImpedida(Base):
    """Model for restricted companies (CEIS/CNEP)."""
    __tablename__ = "empresas_impedidas"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(20), nullable=False, index=True)
    razao_social = Column(String(255))
    fonte = Column(String(10), nullable=False, index=True)  # CEIS ou CNEP
    tipo_sancao = Column(String(100))
    data_inicio_sancao = Column(Date)
    data_fim_sancao = Column(Date, index=True)
    orgao_sancionador = Column(String(255))
    uf_orgao = Column(String(2))
    fundamentacao_legal = Column(Text)
    data_atualizacao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class GovernancaMunicipio(Base):
    """Model for municipality governance KPIs."""
    __tablename__ = "governanca_municipios"
    
    id = Column(Integer, primary_key=True, index=True)
    municipio_id = Column(Integer, ForeignKey("municipios.id"), index=True)
    periodo = Column(String(7), nullable=False, index=True)  # YYYY-MM
    indice_transparencia = Column(Numeric(5, 2))
    taxa_sucesso = Column(Numeric(5, 2))
    tempo_medio_dias = Column(Integer)
    indice_hhi = Column(Numeric(10, 4))
    participacao_meepp = Column(Numeric(5, 2))
    economia_media = Column(Numeric(5, 2))
    total_licitacoes = Column(Integer)
    valor_total = Column(Numeric(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
