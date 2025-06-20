#!/bin/bash

echo "🚀 Iniciando deployment del Blog de Viajes..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mensajes de error
error() {
    echo -e "${RED}❌ Error: $1${NC}"
    exit 1
}

# Función para mensajes de éxito
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mensajes de información
info() {
    echo -e "${YELLOW}ℹ️ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/manage.py" ]; then
    error "No se encuentra manage.py. Ejecuta este script desde la raíz del proyecto."
fi

# Backend
info "Actualizando backend..."
cd backend

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    error "No se encuentra el entorno virtual. Ejecuta: python3 -m venv venv"
fi

# Activar entorno virtual
source venv/bin/activate || error "No se pudo activar el entorno virtual"

# Actualizar código (si estás usando git)
if [ -d ".git" ]; then
    info "Actualizando código desde Git..."
    git pull origin main || git pull origin master
fi

# Instalar/actualizar dependencias
info "Instalando dependencias de Python..."
pip install -r requirements.txt || error "Error instalando dependencias"

# Ejecutar migraciones
info "Ejecutando migraciones de base de datos..."
python manage.py migrate || error "Error en migraciones"

# Recopilar archivos estáticos
info "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput || error "Error recopilando archivos estáticos"

# Volver al directorio raíz
cd ..

# Frontend
info "Actualizando frontend..."
cd frontend

# Instalar/actualizar dependencias de Node.js
info "Instalando dependencias de Node.js..."
npm install || error "Error instalando dependencias de Node.js"

# Construir aplicación React para producción
info "Construyendo aplicación React..."
npm run build || error "Error construyendo aplicación React"

# Volver al directorio raíz
cd ..

# Reiniciar servicios (solo si estamos en el servidor)
if command -v supervisorctl &> /dev/null; then
    info "Reiniciando servicios del servidor..."
    sudo supervisorctl restart blog_gunicorn || info "No se pudo reiniciar Gunicorn (puede que no esté configurado)"
fi

if command -v systemctl &> /dev/null; then
    sudo systemctl reload nginx || info "No se pudo recargar Nginx (puede que no esté configurado)"
fi

success "¡Deployment completado exitosamente!"
echo ""
echo "📝 Pasos siguientes:"
echo "1. Verificar que el sitio funciona correctamente"
echo "2. Probar todas las funcionalidades principales"
echo "3. Verificar que las imágenes se cargan correctamente"
echo "4. Comprobar el mapa de Mapbox"
echo ""
echo "🔗 URLs importantes:"
echo "- Frontend: https://tudominio.com"
echo "- Admin Django: https://tudominio.com/admin"
echo "- API: https://tudominio.com/api" 