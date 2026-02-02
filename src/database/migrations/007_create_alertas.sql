-- Tabela de configuração de alertas
CREATE TABLE IF NOT EXISTS alertas_configuracao (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    tipo VARCHAR(50) NOT NULL,
    palavras_chave JSONB,
    municipios JSONB,
    modalidades JSONB,
    valor_minimo DECIMAL(15,2),
    valor_maximo DECIMAL(15,2),
    canal_notificacao VARCHAR(20) NOT NULL,
    destinatario VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alertas_config_ativo ON alertas_configuracao(ativo);
CREATE INDEX IF NOT EXISTS idx_alertas_config_tipo ON alertas_configuracao(tipo);

-- Tabela de alertas disparados
CREATE TABLE IF NOT EXISTS alertas_disparados (
    id SERIAL PRIMARY KEY,
    configuracao_id INTEGER REFERENCES alertas_configuracao(id) ON DELETE CASCADE,
    licitacao_id INTEGER REFERENCES licitacoes(id),
    mensagem TEXT,
    enviado BOOLEAN DEFAULT false,
    enviado_em TIMESTAMP,
    erro TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alertas_disparados_config ON alertas_disparados(configuracao_id);
CREATE INDEX IF NOT EXISTS idx_alertas_disparados_licitacao ON alertas_disparados(licitacao_id);
CREATE INDEX IF NOT EXISTS idx_alertas_disparados_enviado ON alertas_disparados(enviado);
CREATE INDEX IF NOT EXISTS idx_alertas_disparados_created_at ON alertas_disparados(created_at);

COMMENT ON TABLE alertas_configuracao IS 'Configurações de alertas inteligentes';
COMMENT ON TABLE alertas_disparados IS 'Histórico de alertas disparados';
COMMENT ON COLUMN alertas_configuracao.canal_notificacao IS 'Canal: email, telegram, webhook';
