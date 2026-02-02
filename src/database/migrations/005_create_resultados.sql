-- Create resultados table
CREATE TABLE IF NOT EXISTS resultados (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES itens(id) ON DELETE CASCADE,
    fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id),
    
    data_resultado DATE,
    sequencial_resultado INTEGER,
    
    numero_controle_pncp_compra VARCHAR(100),
    indicador_subcontratacao BOOLEAN DEFAULT FALSE,
    
    percentual_desconto NUMERIC(5, 2),
    quantidade_homologada NUMERIC(15, 4),
    valor_unitario_homologado NUMERIC(15, 2),
    valor_total_homologado NUMERIC(15, 2),
    
    situacao_compra_item_resultado_id INTEGER,
    
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resultados_item ON resultados(item_id);
CREATE INDEX idx_resultados_fornecedor ON resultados(fornecedor_id);
CREATE INDEX idx_resultados_data ON resultados(data_resultado);
