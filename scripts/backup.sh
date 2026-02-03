#!/bin/bash
set -e

# ===========================================
# LAP - Script de Backup do PostgreSQL
# ===========================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Carregar variáveis de ambiente
if [ -f .env ]; then
    source .env
else
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    exit 1
fi

# Definir valores padrão se não estiverem no .env
DB_USER=${DB_USER:-lap_user}
DB_NAME=${DB_NAME:-lap_db}

echo -e "${YELLOW}🔄 Iniciando backup do banco de dados...${NC}"
echo "Data: $(date)"
echo "Banco: $DB_NAME"
echo ""

# Nome do arquivo de backup
BACKUP_FILE="$BACKUP_DIR/lap_backup_${DATE}.sql.gz"

# Executar backup usando docker exec
echo -e "${YELLOW}📦 Criando backup...${NC}"
docker exec lap_postgres pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Verificar se o backup foi criado
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup criado com sucesso!${NC}"
    echo "Arquivo: $BACKUP_FILE"
    echo "Tamanho: $BACKUP_SIZE"
else
    echo -e "${RED}❌ Falha ao criar backup!${NC}"
    exit 1
fi

# Remover backups antigos
echo ""
echo -e "${YELLOW}🧹 Removendo backups antigos (>${RETENTION_DAYS} dias)...${NC}"
find $BACKUP_DIR -name "lap_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# Listar backups existentes
echo ""
echo -e "${YELLOW}📋 Backups existentes:${NC}"
ls -lh $BACKUP_DIR/lap_backup_*.sql.gz 2>/dev/null || echo "Nenhum backup encontrado"

echo ""
echo -e "${GREEN}✅ Processo de backup concluído!${NC}"

# Mostrar como restaurar
echo ""
echo -e "${YELLOW}📖 Para restaurar um backup:${NC}"
echo "   gunzip -c $BACKUP_FILE | docker exec -i lap_postgres psql -U $DB_USER $DB_NAME"
