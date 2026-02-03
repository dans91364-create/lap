-- Migration: Create relatorios table
-- Description: Table for storing generated reports

CREATE TABLE IF NOT EXISTS relatorios (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    formato VARCHAR(10) NOT NULL,
    parametros JSONB,
    filepath VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pendente',
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_relatorios_tipo ON relatorios(tipo);
CREATE INDEX IF NOT EXISTS idx_relatorios_status ON relatorios(status);
CREATE INDEX IF NOT EXISTS idx_relatorios_usuario ON relatorios(usuario_id);
CREATE INDEX IF NOT EXISTS idx_relatorios_created ON relatorios(created_at);

-- Add comment
COMMENT ON TABLE relatorios IS 'Stores generated reports (PDF/Excel) with metadata and status';
