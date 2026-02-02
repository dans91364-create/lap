-- Tabela de empresas impedidas (CEIS/CNEP)
CREATE TABLE IF NOT EXISTS empresas_impedidas (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(20) NOT NULL,
    razao_social VARCHAR(255),
    fonte VARCHAR(10) NOT NULL, -- CEIS ou CNEP
    tipo_sancao VARCHAR(100),
    data_inicio_sancao DATE,
    data_fim_sancao DATE,
    orgao_sancionador VARCHAR(255),
    uf_orgao VARCHAR(2),
    fundamentacao_legal TEXT,
    data_atualizacao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cnpj, fonte)
);

CREATE INDEX IF NOT EXISTS idx_empresas_impedidas_cnpj ON empresas_impedidas(cnpj);
CREATE INDEX IF NOT EXISTS idx_empresas_impedidas_fonte ON empresas_impedidas(fonte);
CREATE INDEX IF NOT EXISTS idx_empresas_impedidas_data_fim ON empresas_impedidas(data_fim_sancao);

COMMENT ON TABLE empresas_impedidas IS 'Empresas com impedimento no CEIS ou CNEP';
COMMENT ON COLUMN empresas_impedidas.fonte IS 'CEIS: Cadastro de Empresas Inidôneas e Suspensas, CNEP: Cadastro Nacional de Empresas Punidas';
