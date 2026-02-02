-- Tabela de anomalias detectadas
CREATE TABLE IF NOT EXISTS anomalias (
    id SERIAL PRIMARY KEY,
    licitacao_id INTEGER REFERENCES licitacoes(id),
    item_id INTEGER,
    fornecedor_id INTEGER,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    valor_detectado DECIMAL(15,2),
    valor_referencia DECIMAL(15,2),
    percentual_desvio DECIMAL(10,2),
    score_risco DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'pendente',
    observacoes TEXT,
    analisado_por VARCHAR(100),
    analisado_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomalias_tipo ON anomalias(tipo);
CREATE INDEX IF NOT EXISTS idx_anomalias_status ON anomalias(status);
CREATE INDEX IF NOT EXISTS idx_anomalias_licitacao ON anomalias(licitacao_id);
CREATE INDEX IF NOT EXISTS idx_anomalias_created_at ON anomalias(created_at);

COMMENT ON TABLE anomalias IS 'Registro de anomalias detectadas em licitações';
COMMENT ON COLUMN anomalias.tipo IS 'Tipo de anomalia: PRECO_ACIMA_MEDIA, FORNECEDOR_RECORRENTE, etc';
COMMENT ON COLUMN anomalias.status IS 'Status: pendente, analisada, descartada';
COMMENT ON COLUMN anomalias.score_risco IS 'Score de risco de 0 a 100';
