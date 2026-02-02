# LAP - Guia de Implantação

## 🚀 Implantação Rápida

### 1. Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espaço em disco

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/dans91364-create/lap.git
cd lap

# Configure as variáveis de ambiente
cp .env.example .env

# Inicie todos os serviços
docker-compose up -d

# Aguarde a inicialização (1-2 minutos)
docker-compose logs -f app
```

### 3. Acesso

- **Dashboard Web**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

### 4. Primeiros Passos

1. Acesse http://localhost:3000
2. O dashboard carregará automaticamente
3. Para executar primeira coleta de dados:

```bash
docker-compose exec app python manage.py coleta:executar
```

## 📊 Verificação da Instalação

### Health Checks

```bash
# Verificar status dos containers
docker-compose ps

# Verificar logs da aplicação
docker-compose logs app

# Verificar logs do frontend
docker-compose logs frontend

# Verificar conexão com banco
docker-compose exec postgres psql -U lap_user -d lap_db -c "SELECT COUNT(*) FROM licitacoes;"
```

### Testar API

```bash
# Health check
curl http://localhost:8000/health

# Listar licitações
curl http://localhost:8000/api/v1/licitacoes/

# Obter KPIs
curl http://localhost:8000/api/v1/estatisticas/kpis
```

## 🔧 Configuração Avançada

### Scheduler de Coletas

O sistema coleta dados automaticamente 4x ao dia. Para alterar:

1. Edite `config/settings.py`
2. Modifique `COLLECTION_TIMES`
3. Reinicie: `docker-compose restart app`

### Alertas por Email

Configure SMTP em `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

### Backup do Banco de Dados

```bash
# Backup
docker-compose exec postgres pg_dump -U lap_user lap_db > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U lap_user lap_db
```

## 🐛 Troubleshooting

### Problema: Frontend não carrega

```bash
# Verificar se frontend está rodando
docker-compose ps frontend

# Reconstruir frontend
docker-compose up -d --build frontend
```

### Problema: API retorna erro 500

```bash
# Verificar logs
docker-compose logs app

# Verificar conexão com banco
docker-compose exec postgres psql -U lap_user -d lap_db -c "\dt"

# Reiniciar serviços
docker-compose restart app postgres
```

### Problema: Migrações não executaram

```bash
# Entrar no container
docker-compose exec postgres psql -U lap_user lap_db

# Listar tabelas
\dt

# Executar migrações manualmente
\i /docker-entrypoint-initdb.d/001_create_municipios.sql
```

## 🔄 Atualizações

```bash
# Parar serviços
docker-compose down

# Atualizar código
git pull origin main

# Reconstruir e reiniciar
docker-compose up -d --build

# Verificar logs
docker-compose logs -f
```

## 📈 Monitoramento

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f app

# Apenas frontend
docker-compose logs -f frontend
```

### Métricas

```bash
# Uso de recursos
docker stats

# Espaço em disco
docker system df
```

## 🔒 Segurança em Produção

### Checklist

- [ ] Alterar senhas padrão no `.env`
- [ ] Configurar HTTPS com certificado SSL
- [ ] Restringir acesso ao pgAdmin
- [ ] Configurar firewall
- [ ] Habilitar backups automáticos
- [ ] Configurar monitoramento
- [ ] Revisar logs de segurança

### HTTPS com Nginx

```bash
# Instalar certbot
apt-get install certbot python3-certbot-nginx

# Obter certificado
certbot --nginx -d seu-dominio.com
```

## 📞 Suporte

Para problemas ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação em /docs
- Verifique logs em `docker-compose logs`
