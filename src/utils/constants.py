"""Constants for the LAP system."""

# PNCP API Endpoints
PNCP_CONTRATACOES_ENDPOINT = "/contratacoes/publicacao"
PNCP_ITENS_ENDPOINT = "/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
PNCP_RESULTADOS_ENDPOINT = "/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numero_item}/resultados"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Date format
PNCP_DATE_FORMAT = "%Y%m%d"
DISPLAY_DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# UF
UF_GOIAS = "GO"

# Collection period (2 years)
COLLECTION_YEARS = 2

# Material ou Serviço
MATERIAL = "M"
SERVICO = "S"

# Tipo Pessoa
PESSOA_JURIDICA = "PJ"
PESSOA_FISICA = "PF"

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Retry Configuration
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 5  # seconds

# Cache TTL (Time To Live)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Export formats
EXPORT_FORMAT_CSV = "csv"
EXPORT_FORMAT_EXCEL = "excel"
EXPORT_FORMAT_JSON = "json"

# Modalidades de Contratação (exemplos)
MODALIDADES = {
    1: "Concorrência",
    2: "Tomada de Preços",
    3: "Convite",
    4: "Concurso",
    5: "Leilão",
    6: "Pregão",
    7: "Dispensa de Licitação",
    8: "Inexigibilidade",
    9: "Credenciamento",
    10: "Pré-qualificação",
    11: "Diálogo Competitivo"
}

# Situações de Compra
SITUACAO_COMPRA = {
    1: "Publicada",
    2: "Aberta",
    3: "Em Análise",
    4: "Homologada",
    5: "Adjudicada",
    6: "Revogada",
    7: "Anulada",
    8: "Suspensa",
    9: "Deserta",
    10: "Fracassada"
}

# Porte Fornecedor
PORTE_ME = "ME"  # Microempresa
PORTE_EPP = "EPP"  # Empresa de Pequeno Porte
PORTE_DEMAIS = "DEMAIS"  # Demais
