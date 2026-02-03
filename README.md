# LAP - Licitações Aparecida Plus

Sistema completo de coleta, análise e visualização de licitações públicas para municípios em um raio de 200km de Goiânia.

## 📋 Visão Geral

O LAP é um sistema automatizado para coleta, armazenamento e análise inteligente de dados de licitações públicas da região de Goiânia e 42 municípios próximos. O sistema coleta dados históricos (2 anos) e mantém atualização contínua através do Portal Nacional de Contratações Públicas (PNCP), com funcionalidades avançadas de detecção de anomalias, alertas inteligentes e análise de governança.

## ✨ Funcionalidades Principais

### Coleta de Dados
- 🔄 **Coleta Automática**: Scheduler executando 4x ao dia (6h, 12h, 18h, 00h)
- 📊 **Dados Completos**: Licitações, itens, vencedores, preços homologados e fornecedores
- 🗺️ **Cobertura Regional**: 43 municípios em raio de 200km de Goiânia
- 📈 **Histórico**: 2 anos de dados retroativos

### Análises Avançadas
- 🚨 **Detecção de Anomalias**: Identificação automática de preços suspeitos, baixa competição, prazos curtos
- 📧 **Alertas Inteligentes**: Sistema configurável de notificações por email/Telegram
- 🏆 **Análise de Governança**: KPIs de transparência, eficiência e concentração de mercado
- 💰 **Análise de Preços**: Estatísticas, tendências, benchmarks regionais e outliers
- ⚠️ **Integração CEIS/CNEP**: Verificação de empresas impedidas

### Dashboard Web
- 📊 **Visualizações Interativas**: Gráficos e mapas com dados em tempo real
- 🔍 **Busca Avançada**: Filtros por município, modalidade, valor, data e palavras-chave
- 📱 **Responsivo**: Design mobile-first com Tailwind CSS
- ⚡ **Performance**: React Query para cache inteligente

## 🏗️ Arquitetura

### Backend (Python)
```
src/
├── api/
│   ├── main.py                 # FastAPI app
│   └── routes/                 # Endpoints REST
│       ├── licitacoes.py
│       ├── anomalias.py
│       ├── alertas.py
│       ├── governanca.py
│       ├── ceis_cnep.py
│       ├── precos.py
│       └── estatisticas.py
├── services/                   # Lógica de negócio
│   ├── anomalia_service.py
│   ├── alerta_service.py
│   ├── governanca_service.py
│   ├── ceis_cnep_service.py
│   └── analise_precos_service.py
├── collectors/                 # Coletores de dados
├── models/                     # Modelos SQLAlchemy
├── database/                   # Conexão e repositórios
│   ├── migrations/             # Scripts SQL (001-009)
│   └── repositories/
└── scheduler/                  # Jobs agendados
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/
│   │   └── layout/
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx       # KPIs e gráficos
│   │   ├── Licitacoes.tsx      # Lista com filtros
│   │   ├── Anomalias.tsx       # Detecção de anomalias
│   │   └── Governanca.tsx      # Ranking de municípios
│   ├── services/
│   │   └── api.ts              # Cliente API
│   └── types/
│       └── index.ts            # TypeScript types
├── Dockerfile
└── nginx.conf
```

## 🚀 Começando

### Pré-requisitos

- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento frontend)
- Python 3.11+ (para desenvolvimento backend)

### Instalação Rápida com Docker

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

3. Inicie todos os serviços:
```bash
docker-compose up -d
```

4. Acesse as interfaces:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

### Desenvolvimento Local

#### Backend
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar migrações
python manage.py migrate

# Iniciar servidor
uvicorn src.api.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar dev server
npm run dev
```

## 📊 API Endpoints

### Licitações
- `GET /api/v1/licitacoes/` - Listar licitações
- `GET /api/v1/licitacoes/{id}` - Detalhes
- `POST /api/v1/licitacoes/search` - Busca avançada

### Anomalias
- `GET /api/v1/anomalias/` - Listar anomalias detectadas
- `GET /api/v1/anomalias/{id}` - Detalhes da anomalia
- `PUT /api/v1/anomalias/{id}/status` - Atualizar status
- `POST /api/v1/anomalias/executar-analise` - Executar análise

### Alertas
- `GET /api/v1/alertas/configuracoes` - Listar configurações
- `POST /api/v1/alertas/configuracoes` - Criar alerta
- `GET /api/v1/alertas/disparados` - Alertas disparados

### Governança
- `GET /api/v1/governanca/kpis` - KPIs de governança
- `GET /api/v1/governanca/ranking` - Ranking de municípios
- `GET /api/v1/governanca/municipio/{id}` - Relatório completo

### CEIS/CNEP
- `GET /api/v1/ceis-cnep/verificar/{cnpj}` - Verificar empresa
- `GET /api/v1/ceis-cnep/empresas-impedidas` - Listar impedidas

### Preços
- `GET /api/v1/precos/historico` - Histórico de preços
- `GET /api/v1/precos/estatisticas` - Estatísticas
- `GET /api/v1/precos/benchmark` - Comparação regional
- `GET /api/v1/precos/sugestao` - Preço de referência

### Estatísticas
- `GET /api/v1/estatisticas/kpis` - KPIs do dashboard
- `GET /api/v1/estatisticas/por-mes` - Licitações por mês
- `GET /api/v1/estatisticas/top-municipios` - Top 10 municípios
- `GET /api/v1/estatisticas/top-fornecedores` - Top 10 fornecedores

## 🗄️ Banco de Dados

### Tabelas Principais
- `municipios` - Municípios da região
- `orgaos` - Órgãos públicos
- `licitacoes` - Licitações públicas
- `itens` - Itens das licitações
- `fornecedores` - Empresas vencedoras
- `resultados` - Resultados e valores homologados

### Tabelas de Análise
- `anomalias` - Anomalias detectadas
- `alertas_configuracao` - Configurações de alertas
- `alertas_disparados` - Histórico de alertas
- `empresas_impedidas` - CEIS/CNEP
- `governanca_municipios` - KPIs por período

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql://lap_user:lap_password@localhost:5432/lap_db

# Redis
REDIS_URL=redis://localhost:6379/0

# PNCP API
PNCP_BASE_URL=https://pncp.gov.br/api/consulta/v1
PNCP_TIMEOUT=30

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=America/Sao_Paulo

# Email (para alertas)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

## 🧪 Testes

```bash
# Backend
pytest

# Frontend
cd frontend
npm test
```

## 📦 Deployment

### Desenvolvimento

Para ambiente de desenvolvimento local:

```bash
docker-compose up -d
```

### Produção

Para deploy em produção (Oracle Cloud, AWS, etc):

```bash
# Clone o repositório
git clone https://github.com/dans91364-create/lap.git
cd lap

# Execute o script de deploy automatizado
./deploy.sh
```

O script irá:
- ✅ Instalar Docker e Docker Compose (se necessário)
- ✅ Criar arquivo `.env` com senhas seguras geradas automaticamente
- ✅ Fazer build das imagens otimizadas para produção
- ✅ Iniciar todos os serviços com configurações de segurança
- ✅ Verificar a saúde da aplicação

**📖 Para instruções completas de deploy, consulte [DEPLOY.md](DEPLOY.md)**

#### Diferenças entre Desenvolvimento e Produção

| Característica | Desenvolvimento | Produção |
|----------------|-----------------|----------|
| Servidor WSGI | Uvicorn com --reload | Gunicorn + Uvicorn workers |
| Workers | 1 worker | 4 workers (configurável) |
| DEBUG | true | false |
| Senhas | Hardcoded | Variáveis de ambiente |
| PostgreSQL | Porta exposta (5432) | Apenas interno |
| Redis | Porta exposta (6379) | Apenas interno |
| pgAdmin | Habilitado | Desabilitado |
| HTTPS | Não | Configurável (Let's Encrypt) |
| Resource Limits | Não | Sim (CPU/Memória) |
| Health Checks | Básico | Completo |
| Logs | INFO | WARNING |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Autores

- [@dans91364-create](https://github.com/dans91364-create)

## 📞 Suporte

Para suporte, abra uma issue no GitHub.

## 🙏 Agradecimentos

- PNCP (Portal Nacional de Contratações Públicas) pela API
- Portal da Transparência (CEIS/CNEP)
- Comunidade open source
