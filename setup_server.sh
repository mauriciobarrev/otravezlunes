#!/bin/bash

echo "🚀 Configurando servidor para OtraVezLunes.com..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
apt update && apt upgrade -y

# Instalar dependencias
echo "🔧 Instalando dependencias..."
apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor git nodejs npm -y

# Crear usuario para la aplicación
echo "👤 Creando usuario blogapp..."
adduser --disabled-password --gecos "" blogapp
usermod -aG sudo blogapp

# Configurar PostgreSQL
echo "🗃️ Configurando base de datos..."
sudo -u postgres psql << EOF
CREATE DATABASE travel_blog_db;
CREATE USER travel_blog_user WITH PASSWORD 'blog123password';
ALTER ROLE travel_blog_user SET client_encoding TO 'utf8';
ALTER ROLE travel_blog_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE travel_blog_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE travel_blog_db TO travel_blog_user;
\q
EOF

# Clonar repositorio
echo "📥 Clonando repositorio..."
sudo -u blogapp git clone https://github.com/mauriciobarrev/otravezlunes.git /home/blogapp/blog

# Configurar backend
echo "🐍 Configurando backend..."
cd /home/blogapp/blog/backend
sudo -u blogapp python3 -m venv venv
sudo -u blogapp venv/bin/pip install -r requirements.txt

# Crear archivo .env de producción
sudo -u blogapp cat > /home/blogapp/blog/backend/.env.production << EOF
SECRET_KEY='4r=5-tx+id%n&yl3\$!fo8o\$waq8w(pyf=#p6!(7qz019b(rw2r'
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=travel_blog_db
DB_USER=travel_blog_user
DB_PASSWORD=blog123password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=otravezlunes.com,www.otravezlunes.com,157.230.111.57
CORS_ALLOWED_ORIGINS=https://otravezlunes.com,https://www.otravezlunes.com
EOF

# Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
cd /home/blogapp/blog/backend
sudo -u blogapp venv/bin/python manage.py migrate
sudo -u blogapp venv/bin/python manage.py collectstatic --noinput

# Configurar frontend
echo "⚛️ Configurando frontend..."
cd /home/blogapp/blog/frontend
sudo -u blogapp cat > .env.production << EOF
REACT_APP_API_URL=https://otravezlunes.com/api
REACT_APP_MAPBOX_TOKEN=pk.eyJ1IjoibWF1cmljaW9iYXJyZXYiLCJhIjoiY21hdTl3bG53MTVpMjJxb3Njd2xoM2VuMiJ9.piVsma3PVk8ZcTcy4fLEng
GENERATE_SOURCEMAP=false
EOF

sudo -u blogapp npm install
sudo -u blogapp npm run build

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/otravezlunes << EOF
server {
    listen 80;
    server_name otravezlunes.com www.otravezlunes.com 157.230.111.57;

    # Frontend estático
    location / {
        root /home/blogapp/blog/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Admin Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Archivos media (fotos)
    location /media/ {
        alias /home/blogapp/blog/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Archivos estáticos Django
    location /static/ {
        alias /home/blogapp/blog/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -s /etc/nginx/sites-available/otravezlunes /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# Configurar Supervisor
echo "⚙️ Configurando Supervisor..."
cat > /etc/supervisor/conf.d/otravezlunes.conf << EOF
[program:otravezlunes_gunicorn]
command=/home/blogapp/blog/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 core_project.wsgi:application
directory=/home/blogapp/blog/backend
user=blogapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/otravezlunes_gunicorn.log
environment=DJANGO_SETTINGS_MODULE=core_project.settings
EOF

# Reiniciar servicios
echo "🔄 Reiniciando servicios..."
supervisorctl reread
supervisorctl update
supervisorctl start otravezlunes_gunicorn
systemctl restart nginx

# Configurar permisos
chown -R blogapp:blogapp /home/blogapp/blog/

echo "✅ ¡Configuración completada!"
echo ""
echo "🎉 Tu blog debería estar funcionando en:"
echo "http://157.230.111.57"
echo "http://otravezlunes.com (cuando configures el DNS)"
echo ""
echo "🔧 Para crear un superusuario:"
echo "sudo -u blogapp /home/blogapp/blog/backend/venv/bin/python /home/blogapp/blog/backend/manage.py createsuperuser" 