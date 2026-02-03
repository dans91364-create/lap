-- Migration: Create usuarios table
-- Description: Table for storing system users with authentication

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    perfil VARCHAR(50) DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios(ativo);

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION)
-- Password hash generated with bcrypt
INSERT INTO usuarios (nome, email, senha_hash, perfil) 
VALUES (
    'Administrador',
    'admin@lap.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWP0VVZWKm',
    'admin'
) ON CONFLICT (email) DO NOTHING;
