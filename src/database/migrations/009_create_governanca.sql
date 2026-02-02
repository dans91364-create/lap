-- Tabela de KPIs de governança por município
CREATE TABLE IF NOT EXISTS governanca_municipios (
    id SERIAL PRIMARY KEY,
    municipio_id INTEGER REFERENCES municipios(id),
    periodo VARCHAR(7) NOT NULL, -- YYYY-MM
    indice_transparencia DECIMAL(5,2),
    taxa_sucesso DECIMAL(5,2),
    tempo_medio_dias INTEGER,
    indice_hhi DECIMAL(10,4),
    participacao_meepp DECIMAL(5,2),
    economia_media DECIMAL(5,2),
    total_licitacoes INTEGER,
    valor_total DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(municipio_id, periodo)
);

CREATE INDEX IF NOT EXISTS idx_governanca_municipio ON governanca_municipios(municipio_id);
CREATE INDEX IF NOT EXISTS idx_governanca_periodo ON governanca_municipios(periodo);

COMMENT ON TABLE governanca_municipios IS 'Indicadores de governança por município e período';
COMMENT ON COLUMN governanca_municipios.indice_transparencia IS 'Índice de transparência (0-100) baseado na completude dos dados';
COMMENT ON COLUMN governanca_municipios.taxa_sucesso IS 'Percentual de licitações concluídas vs desertadas/fracassadas';
COMMENT ON COLUMN governanca_municipios.tempo_medio_dias IS 'Dias médios entre publicação e homologação';
COMMENT ON COLUMN governanca_municipios.indice_hhi IS 'Índice Herfindahl-Hirschman de concentração de mercado';
COMMENT ON COLUMN governanca_municipios.participacao_meepp IS 'Percentual de vitórias de ME/EPP';
COMMENT ON COLUMN governanca_municipios.economia_media IS 'Percentual médio de economia (estimado vs homologado)';
