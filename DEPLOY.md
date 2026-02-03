# 🚀 Guia de Deploy em Produção - Oracle Cloud

Este guia detalha o processo completo de deploy do sistema LAP em produção na Oracle Cloud Free Tier.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Preparação da VM Oracle Cloud](#preparação-da-vm-oracle-cloud)
- [Deploy do Sistema](#deploy-do-sistema)
- [Configuração de Firewall](#configuração-de-firewall)
- [Configuração SSL/HTTPS (Opcional)](#configuração-sslhttps-opcional)
- [Monitoramento e Manutenção](#monitoramento-e-manutenção)
- [Backup e Restore](#backup-e-restore)
- [Troubleshooting](#troubleshooting)
- [Comandos Úteis](#comandos-úteis)

---

## 🔧 Pré-requisitos

### Recursos Oracle Cloud Free Tier
- **VM ARM**: 2 OCPU + 12GB RAM (Ampere A1)
- **Storage**: 200GB Boot Volume
- **IP Público**: 1 IP público permanente
- **Banda**: Tráfego ilimitado de saída

### Conhecimentos Necessários
- Noções básicas de Linux
- SSH para conexão remota
- Conceitos de Docker

---

## 🖥️ Preparação da VM Oracle Cloud

### 1. Criar a VM

1. Acesse o [Console Oracle Cloud](https://cloud.oracle.com/)
2. Navegue até **Compute** > **Instances** > **Create Instance**
3. Configure:
   - **Name**: `lap-production`
   - **Image**: Ubuntu 22.04 LTS (ARM)
   - **Shape**: VM.Standard.A1.Flex (2 OCPU, 12GB RAM)
   - **Boot Volume**: 200GB
   - **SSH Keys**: Adicione sua chave pública SSH

### 2. Configurar Security List (Firewall Oracle Cloud)

No painel da VM, acesse **Virtual Cloud Network** > **Security Lists** e adicione as regras:

| Tipo | Protocol | Source | Port Range | Descrição |
|------|----------|--------|------------|-----------|
| Ingress | TCP | 0.0.0.0/0 | 22 | SSH |
| Ingress | TCP | 0.0.0.0/0 | 80 | HTTP |
| Ingress | TCP | 0.0.0.0/0 | 443 | HTTPS (se usar SSL) |

### 3. Conectar via SSH

```bash
ssh -i ~/.ssh/sua_chave_privada ubuntu@SEU_IP_PUBLICO
```

### 4. Atualizar o Sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget
```

---

## 🚀 Deploy do Sistema

### 1. Clonar o Repositório

```bash
cd ~
git clone https://github.com/dans91364-create/lap.git
cd lap
```

### 2. Executar o Script de Deploy

O script `deploy.sh` automatiza todo o processo:

```bash
./deploy.sh
```

#### O que o script faz:

1. ✅ Verifica e instala Docker (se necessário)
2. ✅ Verifica e instala Docker Compose (se necessário)
3. ✅ Cria arquivo `.env` a partir do template
4. ✅ Gera automaticamente `SECRET_KEY` e senha do banco
5. ✅ Cria diretórios necessários
6. ✅ Faz build das imagens Docker
7. ✅ Inicia todos os containers
8. ✅ Verifica a saúde dos serviços

### 3. Configurar Variáveis de Ambiente

Após a primeira execução, edite o arquivo `.env`:

```bash
nano .env
```

**Configurações obrigatórias:**

```env
# Altere para seu IP público ou domínio
API_URL=http://SEU_IP_PUBLICO

# Já geradas automaticamente - NÃO ALTERE
DB_PASSWORD=senha_gerada_automaticamente
SECRET_KEY=chave_gerada_automaticamente
```

**Configurações opcionais:**

```env
# Email (se quiser alertas por email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
SMTP_FROM=noreply@seudominio.com

# Telegram (se quiser alertas no Telegram)
TELEGRAM_BOT_TOKEN=seu_token_do_bot
```

### 4. Reiniciar os Serviços

Após editar o `.env`, reinicie os containers:

```bash
docker-compose -f docker-compose.prod.yml restart
```

---

## 🔥 Configuração de Firewall

### Firewall do Ubuntu (UFW)

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH (IMPORTANTE: faça isso primeiro!)
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS (se usar SSL)
sudo ufw allow 443/tcp

# Verificar status
sudo ufw status
```

### Firewall Oracle Cloud

As regras já foram configuradas no Security List (Passo 1.2).

---

## 🔒 Configuração SSL/HTTPS (Opcional)

### Opção 1: Certbot (Let's Encrypt) - Recomendado

**1. Instalar Certbot:**

```bash
sudo apt install -y certbot
```

**2. Parar temporariamente o Nginx:**

```bash
docker-compose -f docker-compose.prod.yml stop frontend
```

**3. Gerar certificado:**

```bash
sudo certbot certonly --standalone -d seu-dominio.com
```

**4. Copiar certificados:**

```bash
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/*.pem
```

**5. Descomentar configuração HTTPS no `nginx/nginx.prod.conf`:**

```nginx
# Remova os comentários (#) do bloco server { listen 443 ssl http2; ... }
```

**6. Ativar redirecionamento HTTP → HTTPS:**

No bloco `server { listen 80; ... }`, descomente:

```nginx
return 301 https://$server_name$request_uri;
```

**7. Reiniciar frontend:**

```bash
docker-compose -f docker-compose.prod.yml up -d frontend
```

**8. Renovação automática:**

Adicione ao crontab:

```bash
sudo crontab -e
```

```
0 0 * * * certbot renew --quiet --post-hook "docker-compose -f $(pwd)/docker-compose.prod.yml restart frontend"
```

**Note:** Replace `$(pwd)` with the full path to your LAP installation directory (e.g., `/home/ubuntu/lap`).

### Opção 2: Cloudflare (Alternativa Gratuita)

1. Adicione seu domínio ao Cloudflare
2. Configure os nameservers
3. Ative SSL/TLS no modo "Full"
4. Cloudflare gerencia SSL automaticamente

---

## 📊 Monitoramento e Manutenção

### Verificar Status dos Containers

```bash
docker-compose -f docker-compose.prod.yml ps
```

### Ver Logs

```bash
# Todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Apenas API
docker-compose -f docker-compose.prod.yml logs -f app

# Apenas Frontend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Apenas PostgreSQL
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Verificar Uso de Recursos

```bash
# CPU e Memória dos containers
docker stats

# Espaço em disco
df -h

# Uso de disco pelos volumes Docker
docker system df
```

### Verificar Saúde da API

```bash
curl http://localhost/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

---

## 💾 Backup e Restore

### Backup Manual

```bash
./scripts/backup.sh
```

O backup será salvo em `./backups/lap_backup_YYYYMMDD_HHMMSS.sql.gz`

### Backup Automático (Cron)

Adicione ao crontab para backup diário às 3h da manhã:

```bash
crontab -e
```

```
0 3 * * * cd $(pwd) && ./scripts/backup.sh >> /var/log/lap-backup.log 2>&1
```

**Note:** Replace `$(pwd)` with the full path to your LAP installation directory (e.g., `/home/ubuntu/lap`).

### Restore do Backup

```bash
# Parar a aplicação
docker-compose -f docker-compose.prod.yml stop app

# Restaurar backup
gunzip -c ./backups/lap_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i lap_postgres psql -U lap_user lap_db

# Reiniciar aplicação
docker-compose -f docker-compose.prod.yml start app
```

### Backup para Storage Externo

Para Oracle Object Storage ou outro serviço:

```bash
# Instalar OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configurar
oci setup config

# Upload do backup
oci os object put --bucket-name lap-backups \
  --file ./backups/lap_backup_$(date +%Y%m%d).sql.gz
```

---

## 🔧 Troubleshooting

### Problema: Containers não iniciam

**Verificar logs:**
```bash
docker-compose -f docker-compose.prod.yml logs
```

**Verificar se há containers conflitantes:**
```bash
docker ps -a
```

**Remover containers antigos:**
```bash
docker-compose -f docker-compose.prod.yml down
docker system prune -a
```

### Problema: API não responde

**1. Verificar se o container está rodando:**
```bash
docker ps | grep lap_app
```

**2. Verificar logs da API:**
```bash
docker logs lap_app --tail 100
```

**3. Verificar conexão com banco:**
```bash
docker exec lap_app curl http://localhost:8000/health
```

### Problema: Banco de dados não conecta

**1. Verificar se PostgreSQL está rodando:**
```bash
docker ps | grep lap_postgres
```

**2. Testar conexão:**
```bash
docker exec lap_postgres pg_isready -U lap_user
```

**3. Verificar variáveis de ambiente:**
```bash
docker exec lap_app env | grep DATABASE
```

### Problema: Sem espaço em disco

**1. Limpar logs do Docker:**
```bash
sudo sh -c "truncate -s 0 /var/lib/docker/containers/*/*-json.log"
```

**2. Remover imagens não utilizadas:**
```bash
docker image prune -a
```

**3. Remover volumes órfãos:**
```bash
docker volume prune
```

### Problema: Alto uso de memória

**1. Verificar uso:**
```bash
docker stats --no-stream
```

**2. Ajustar limites no `docker-compose.prod.yml`:**
```yaml
deploy:
  resources:
    limits:
      memory: 512M  # Reduzir se necessário
```

**3. Reiniciar containers:**
```bash
docker-compose -f docker-compose.prod.yml restart
```

---

## 📝 Comandos Úteis

### Docker Compose

```bash
# Iniciar todos os serviços
docker-compose -f docker-compose.prod.yml up -d

# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Reiniciar serviços
docker-compose -f docker-compose.prod.yml restart

# Rebuild e restart
docker-compose -f docker-compose.prod.yml up -d --build

# Ver status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Escalar workers (exemplo)
docker-compose -f docker-compose.prod.yml up -d --scale app=2
```

### Docker

```bash
# Listar containers
docker ps

# Parar container específico
docker stop lap_app

# Iniciar container específico
docker start lap_app

# Executar comando em container
docker exec -it lap_app bash

# Ver logs de container
docker logs -f lap_app

# Inspecionar container
docker inspect lap_app

# Remover container
docker rm lap_app

# Remover imagem
docker rmi lap_app
```

### PostgreSQL

```bash
# Acessar psql
docker exec -it lap_postgres psql -U lap_user -d lap_db

# Fazer dump do banco
docker exec lap_postgres pg_dump -U lap_user lap_db > backup.sql

# Restaurar dump
cat backup.sql | docker exec -i lap_postgres psql -U lap_user lap_db

# Ver tabelas
docker exec lap_postgres psql -U lap_user -d lap_db -c "\dt"

# Ver conexões ativas
docker exec lap_postgres psql -U lap_user -d lap_db -c "SELECT * FROM pg_stat_activity;"
```

### Sistema

```bash
# Ver uso de CPU e memória
htop

# Ver uso de disco
df -h

# Ver processos Docker
ps aux | grep docker

# Ver portas abertas
sudo netstat -tulpn | grep LISTEN

# Verificar memória disponível
free -h

# Ver logs do sistema
sudo journalctl -xe
```

---

## 🆘 Suporte

### Links Úteis

- **Documentação Oracle Cloud**: https://docs.oracle.com/en-us/iaas/
- **Docker Documentation**: https://docs.docker.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

### Checklist de Verificação Pós-Deploy

- [ ] Containers estão rodando: `docker ps`
- [ ] API responde: `curl http://localhost/health`
- [ ] Frontend carrega: `curl http://localhost`
- [ ] Banco de dados conecta
- [ ] Logs não mostram erros críticos
- [ ] Firewall configurado corretamente
- [ ] .env configurado com senhas fortes
- [ ] Backup automático agendado
- [ ] Recursos de CPU/Memória dentro do limite

### Melhorias Futuras

- [ ] Configurar HTTPS com Let's Encrypt
- [ ] Implementar reverse proxy com Traefik
- [ ] Adicionar Prometheus + Grafana para monitoramento
- [ ] Configurar alertas automáticos
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar balanceamento de carga
- [ ] Configurar replicação do PostgreSQL

---

**Desenvolvido com ❤️ para a comunidade de Aparecida de Goiânia**
