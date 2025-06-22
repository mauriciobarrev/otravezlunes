#!/bin/bash

# Script para ejecutar el proyecto en modo desarrollo
# Este script permite testing desde dispositivos móviles

echo "🚀 Iniciando el proyecto de blog de viajes en modo desarrollo..."

# Obtener la IP local para testing móvil
LOCAL_IP=$(ifconfig | grep -E 'inet.*broadcast' | awk '{print $2}' | head -1)
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

echo "📱 Para probar en móvil, usa: http://$LOCAL_IP:3000"
echo "💻 Para probar en local, usa: http://localhost:3000"

# No configurar token por defecto - dejamos que React use el .env o el fallback interno
echo "📍 El token de Mapbox se manejará desde el archivo .env o fallback interno"

# Ejecutar el backend en background
echo "🔧 Iniciando el backend..."
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Esperar a que el backend esté listo
sleep 3

# Ejecutar el frontend
echo "🎨 Iniciando el frontend..."
cd ../frontend
# Configurar para aceptar conexiones desde cualquier IP
HOST=0.0.0.0 npm start &
FRONTEND_PID=$!

# Mostrar información de conexión
echo ""
echo "✅ Servicios iniciados:"
echo "   Backend: http://$LOCAL_IP:8000 (también http://localhost:8000)"
echo "   Frontend: http://$LOCAL_IP:3000 (también http://localhost:3000)"
echo ""
echo "📱 Para conectar desde tu iPhone:"
echo "   1. Asegúrate de estar en la misma red WiFi"
echo "   2. Abre Safari y ve a: http://$LOCAL_IP:3000"
echo ""
echo "⏹️  Presiona Ctrl+C para detener ambos servicios"

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C
trap cleanup INT

# Esperar a que el usuario presione Ctrl+C
wait 