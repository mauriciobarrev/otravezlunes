#!/bin/bash

# Script de Backup para Blog de Viajes
# Ejecutar diariamente con cron

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/blogapp/backups"
DB_NAME="travel_blog_db"
DB_USER="travel_blog_user"
PROJECT_DIR="/home/blogapp/blog"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() {
    echo -e "${YELLOW}ℹ️ $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

info "Iniciando backup del Blog de Viajes - $DATE"

# 1. Backup de la base de datos
info "Creando backup de la base de datos..."
pg_dump -h localhost -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql
if [ $? -eq 0 ]; then
    success "Backup de base de datos completado"
else
    echo "❌ Error en backup de base de datos"
fi

# 2. Backup de archivos media (fotos)
info "Creando backup de archivos media..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz $PROJECT_DIR/media/
if [ $? -eq 0 ]; then
    success "Backup de archivos media completado"
else
    echo "❌ Error en backup de archivos media"
fi

# 3. Backup del código fuente (opcional)
info "Creando backup del código fuente..."
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz $PROJECT_DIR --exclude="$PROJECT_DIR/backend/venv" --exclude="$PROJECT_DIR/frontend/node_modules" --exclude="$PROJECT_DIR/media"
if [ $? -eq 0 ]; then
    success "Backup de código fuente completado"
else
    echo "❌ Error en backup de código fuente"
fi

# 4. Limpiar backups antiguos (mantener solo los últimos 7 días)
info "Limpiando backups antiguos..."
find $BACKUP_DIR -name "*backup*" -type f -mtime +7 -delete
success "Limpieza de backups antiguos completada"

# 5. Mostrar información del backup
info "Información del backup:"
ls -lh $BACKUP_DIR/*$DATE*

success "Backup completado exitosamente - $DATE"

# Opcional: Enviar backup a almacenamiento en la nube
# Descomenta las siguientes líneas si usas rsync o aws s3
# rsync -avz $BACKUP_DIR/ usuario@servidor-backup:/ruta/backups/
# aws s3 sync $BACKUP_DIR/ s3://mi-bucket-backup/blog-backups/ 