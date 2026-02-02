-- Create itens table
CREATE TABLE IF NOT EXISTS itens (
    id SERIAL PRIMARY KEY,
    licitacao_id INTEGER NOT NULL REFERENCES licitacoes(id) ON DELETE CASCADE,
    
    numero_item INTEGER NOT NULL,
    material_ou_servico VARCHAR(1),
    
    tipo_beneficio_id INTEGER,
    tipo_beneficio_nome VARCHAR(100),
    
    incentivo_produtivo_basico BOOLEAN DEFAULT FALSE,
    
    descricao TEXT NOT NULL,
    quantidade NUMERIC(15, 4),
    unidade_medida VARCHAR(50),
    
    valor_unitario_estimado NUMERIC(15, 2),
    valor_total NUMERIC(15, 2),
    
    situacao_compra_item_id INTEGER,
    situacao_compra_item_nome VARCHAR(100),
    
    criterio_julgamento_id INTEGER,
    criterio_julgamento_nome VARCHAR(100),
    
    codigo_produto VARCHAR(50),
    orcamento_sigiloso BOOLEAN DEFAULT FALSE,
    item_categoria_id INTEGER,
    item_categoria_nome VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_itens_licitacao ON itens(licitacao_id);
CREATE INDEX idx_itens_numero ON itens(numero_item);
CREATE INDEX idx_itens_descricao ON itens USING gin(to_tsvector('portuguese', descricao));
