#!/bin/bash
set -e

# ===========================================
# LAP - Script de Deploy para Produção
# ===========================================

echo "🚀 LAP - Deploy para Produção"
echo "================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Não execute como root. Use um usuário normal com sudo.${NC}"
    exit 1
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Instalando Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker instalado. Faça logout e login novamente, depois execute o script de novo.${NC}"
    exit 0
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Instalando Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo -e "${YELLOW}📋 Criando a partir do template...${NC}"
    cp .env.production.example .env
    
    # Gerar SECRET_KEY automaticamente
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/GERE_UMA_CHAVE_SECRETA_COM_OPENSSL/$SECRET_KEY/" .env
    
    # Gerar senha do banco automaticamente
    DB_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    sed -i "s/ALTERE_ESTA_SENHA_FORTE_AQUI/$DB_PASSWORD/" .env
    
    echo -e "${GREEN}✅ Arquivo .env criado com senhas geradas automaticamente.${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edite o arquivo .env e configure API_URL com seu IP/domínio!${NC}"
    echo -e "${YELLOW}   nano .env${NC}"
    exit 0
fi

# Criar diretórios necessários
echo -e "${YELLOW}📁 Criando diretórios...${NC}"
mkdir -p nginx/ssl
mkdir -p backups

# Parar containers existentes
echo -e "${YELLOW}🛑 Parando containers existentes...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build das imagens
echo -e "${YELLOW}🔨 Construindo imagens...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar containers
echo -e "${YELLOW}🚀 Iniciando containers...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Aguardar serviços ficarem prontos
echo -e "${YELLOW}⏳ Aguardando serviços iniciarem...${NC}"
sleep 10

# Verificar status
echo -e "${YELLOW}📊 Verificando status dos serviços...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Verificar health
echo ""
echo -e "${YELLOW}🏥 Verificando saúde da API...${NC}"
sleep 5
if curl -s http://localhost/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API está funcionando!${NC}"
else
    echo -e "${RED}⚠️  API ainda está iniciando ou com problemas. Verifique os logs:${NC}"
    echo "   docker-compose -f docker-compose.prod.yml logs app"
fi

# Mostrar informações finais
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "📊 Dashboard: http://$(hostname -I | awk '{print $1}')"
echo -e "📡 API: http://$(hostname -I | awk '{print $1}')/api/v1"
echo -e "🔍 Health: http://$(hostname -I | awk '{print $1}')/health"
echo ""
echo -e "${YELLOW}📋 Comandos úteis:${NC}"
echo "   Ver logs:        docker-compose -f docker-compose.prod.yml logs -f"
echo "   Reiniciar:       docker-compose -f docker-compose.prod.yml restart"
echo "   Parar:           docker-compose -f docker-compose.prod.yml down"
echo "   Status:          docker-compose -f docker-compose.prod.yml ps"
echo ""
