#!/bin/bash

# Función para detener los procesos al terminar
cleanup() {
    echo "Terminando procesos..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Detectar Ctrl+C para detener procesos
trap cleanup INT TERM

# Iniciar el backend
echo "Iniciando el backend Django..."
cd backend
source venv/bin/activate
python manage.py runserver 8000 &
BACKEND_PID=$!
cd ..

# Iniciar el frontend
echo "Iniciando el frontend React..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Ambos servidores están ejecutándose."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Presiona Ctrl+C para detener ambos servidores."

# Mantener el script activo hasta que el usuario lo detenga
wait 