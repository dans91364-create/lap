-- Create fornecedores table
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    cnpj_cpf VARCHAR(14) UNIQUE NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    
    porte_fornecedor_id INTEGER,
    porte_fornecedor_nome VARCHAR(50),
    
    tipo_pessoa VARCHAR(2),
    
    municipio VARCHAR(100),
    uf VARCHAR(2),
    codigo_pais VARCHAR(10),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fornecedores_cnpj_cpf ON fornecedores(cnpj_cpf);
CREATE INDEX idx_fornecedores_razao_social ON fornecedores(razao_social);
CREATE INDEX idx_fornecedores_uf ON fornecedores(uf);
