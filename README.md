# LAP - Licitações Aparecida Plus

Sistema completo de coleta de licitações públicas para municípios em um raio de 200km de Goiânia.

## 📋 Visão Geral

O LAP é um sistema automatizado para coleta, armazenamento e análise de dados de licitações públicas da região de Goiânia e 42 municípios próximos. O sistema coleta dados históricos (2 anos) e mantém atualização contínua através do Portal Nacional de Contratações Públicas (PNCP).

## ✨ Funcionalidades

- 🔄 **Coleta Automática**: Scheduler executando 4x ao dia (6h, 12h, 18h, 00h)
- 📊 **Dados Completos**: Licitações, itens, vencedores, preços homologados e fornecedores
- 🗺️ **Cobertura Regional**: 43 municípios em raio de 200km de Goiânia
- 📈 **API REST**: Interface completa para consultas e análises
- 🔍 **Busca Avançada**: Filtros por município, modalidade, valor, data e palavras-chave
- 📦 **Docker**: Ambiente containerizado com PostgreSQL, Redis e pgAdmin

## 🏗️ Arquitetura

```
lap/
├── src/
│   ├── collectors/          # Coletores de dados (PNCP API)
│   ├── models/              # Modelos SQLAlchemy
│   ├── database/            # Conexão e repositórios
│   ├── api/                 # FastAPI routes e schemas
│   ├── services/            # Lógica de negócio
│   ├── scheduler/           # Jobs agendados
│   └── utils/               # Utilitários
├── config/                  # Configurações e municípios
├── tests/                   # Testes
└── docker-compose.yml       # Orquestração de containers
```

## 🚀 Começando

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)

### Instalação com Docker

1. Clone o repositório:
```bash
git clone https://github.com/dans91364-create/lap.git
cd lap
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env conforme necessário
```

3. Inicie os containers:
```bash
docker-compose up -d
```

4. A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

### Instalação Local

1. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

4. Execute as migrações:
```bash
# As tabelas serão criadas automaticamente ao iniciar a aplicação
```

5. Inicie a aplicação:
```bash
uvicorn src.api.main:app --reload
```

## 📚 Uso

### Carregar Municípios

```python
from src.services.coleta_service import ColetaService

service = ColetaService()
await service.load_municipios_from_config()
```

### Coletar Licitações

```python
# Coletar para um município específico
await service.collect_licitacoes_for_municipio("5208707", years=2)

# Coletar para todos os municípios
stats = await service.collect_all_municipios(years=2)
print(stats)
```

### API Endpoints

#### Listar Licitações
```bash
GET /api/v1/licitacoes/?skip=0&limit=100
```

#### Buscar Licitações
```bash
POST /api/v1/licitacoes/search
{
  "municipio_id": 1,
  "modalidade_id": 6,
  "palavra_chave": "pavimentação"
}
```

#### Listar Municípios
```bash
GET /api/v1/municipios/
```

#### Detalhes de Licitação
```bash
GET /api/v1/licitacoes/{id}
```

## 🗄️ Banco de Dados

### Estrutura

- **municipios**: Municípios da região
- **orgaos**: Órgãos públicos (entidades)
- **licitacoes**: Processos licitatórios
- **itens**: Itens das licitações
- **fornecedores**: Fornecedores/Vencedores
- **resultados**: Resultados por item

### Relacionamentos

```
Municipio 1---N Licitacao
Orgao 1---N Licitacao
Licitacao 1---N Item
Item 1---N Resultado
Fornecedor 1---N Resultado
```

## 🔧 Configuração

### Variáveis de Ambiente

- **DATABASE_URL**: String de conexão PostgreSQL
- **REDIS_URL**: URL do Redis
- **PNCP_BASE_URL**: URL base da API PNCP
- **SCHEDULER_ENABLED**: Habilitar/desabilitar scheduler
- **COLLECTION_TIMES**: Horários de coleta (ex: "06:00,12:00,18:00,00:00")

### Municípios Cobertos

O sistema cobre 43 municípios em Goiás:
- Goiânia (0km)
- Aparecida de Goiânia (10km)
- Anápolis (55km)
- ... até 200km de raio

Veja a lista completa em `config/municipios_200km.json`

## 🧪 Testes

```bash
pytest tests/
```

## 📖 Documentação da API

Acesse a documentação interativa em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔗 Fontes de Dados

- **PNCP API**: https://pncp.gov.br/api/consulta/v1
- **Documentação**: https://pncp.gov.br/api/consulta/swaggerui/index.html

## 📊 Dados Coletados

### Licitação
- Dados básicos (número, processo, modalidade)
- Órgão e unidade responsável
- Objeto e descrição
- Valores estimados e homologados
- Datas (publicação, abertura, encerramento)
- Situação e resultado

### Itens
- Descrição e quantidade
- Valores unitários e totais
- Categoria e classificação
- Critério de julgamento

### Resultados
- Fornecedor vencedor
- Valores homologados
- Quantidade e descontos
- Situação do resultado

## 🛠️ Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **Redis** - Cache
- **Docker** - Containerização
- **APScheduler** - Agendamento de tarefas
- **HTTPX** - Cliente HTTP assíncrono

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📧 Contato

Para dúvidas e sugestões, abra uma issue no repositório.