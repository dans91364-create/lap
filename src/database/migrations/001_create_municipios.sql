-- Create municipios table
CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    codigo_ibge VARCHAR(7) UNIQUE NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    uf VARCHAR(2) NOT NULL,
    distancia_km INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_municipios_codigo_ibge ON municipios(codigo_ibge);
CREATE INDEX idx_municipios_uf ON municipios(uf);
