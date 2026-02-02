-- Create orgaos table
CREATE TABLE IF NOT EXISTS orgaos (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    poder_id VARCHAR(20),
    esfera_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orgaos_cnpj ON orgaos(cnpj);

-- Create licitacoes table
CREATE TABLE IF NOT EXISTS licitacoes (
    id SERIAL PRIMARY KEY,
    sequencial_compra VARCHAR(20),
    numero_compra VARCHAR(50),
    processo VARCHAR(50),
    ano_compra INTEGER,
    numero_controle_pncp VARCHAR(100) UNIQUE,
    
    orgao_id INTEGER REFERENCES orgaos(id),
    municipio_id INTEGER REFERENCES municipios(id),
    
    modalidade_id INTEGER,
    modalidade_nome VARCHAR(100),
    
    modo_disputa_id INTEGER,
    modo_disputa_nome VARCHAR(100),
    
    tipo_instrumento_convocatorio_nome VARCHAR(100),
    
    amparo_legal_descricao TEXT,
    amparo_legal_nome VARCHAR(255),
    amparo_legal_codigo VARCHAR(50),
    
    objeto_compra TEXT,
    informacao_complementar TEXT,
    
    srp BOOLEAN DEFAULT FALSE,
    
    data_publicacao_pncp TIMESTAMP,
    data_abertura_proposta TIMESTAMP,
    data_encerramento_proposta TIMESTAMP,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP,
    
    situacao_compra_id INTEGER,
    situacao_compra_nome VARCHAR(100),
    
    valor_total_estimado NUMERIC(15, 2),
    valor_total_homologado NUMERIC(15, 2),
    
    link_sistema_origem TEXT,
    justificativa_presencial TEXT,
    existe_resultado BOOLEAN DEFAULT FALSE,
    orcamento_sigiloso_codigo VARCHAR(10),
    usuario_nome VARCHAR(255),
    
    unidade_codigo VARCHAR(20),
    unidade_nome VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_licitacoes_numero_controle ON licitacoes(numero_controle_pncp);
CREATE INDEX idx_licitacoes_orgao ON licitacoes(orgao_id);
CREATE INDEX idx_licitacoes_municipio ON licitacoes(municipio_id);
CREATE INDEX idx_licitacoes_data_publicacao ON licitacoes(data_publicacao_pncp);
CREATE INDEX idx_licitacoes_modalidade ON licitacoes(modalidade_id);
CREATE INDEX idx_licitacoes_ano ON licitacoes(ano_compra);
