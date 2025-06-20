# 🚀 Guía Completa para Publicar tu Blog de Viajes en Internet

## 📋 Índice
1. [Prerrequisitos](#prerrequisitos)
2. [Configuración de Producción](#configuración-de-producción)
3. [Opciones de Hosting](#opciones-de-hosting)
4. [Deployment Paso a Paso](#deployment-paso-a-paso)
5. [Configuración de Dominio](#configuración-de-dominio)
6. [Mantenimiento y Monitoreo](#mantenimiento-y-monitoreo)

## 🔧 Prerrequisitos

Tu proyecto ya está bien estructurado, pero necesitas:

### 1. Archivos de Configuración Faltantes

#### Archivo `.env` para Producción
Necesitas crear archivos `.env` separados para desarrollo y producción:

**backend/.env.development** (para desarrollo local):
```env
SECRET_KEY=tu_clave_secreta_desarrollo
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

**backend/.env.production** (para producción):
```env
SECRET_KEY=tu_clave_secreta_super_segura_de_50_caracteres
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nombre_base_datos_produccion
DB_USER=usuario_db
DB_PASSWORD=contraseña_super_segura
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### 2. Dependencias Adicionales para Producción

Actualizar `backend/requirements.txt`:
```txt
# ... dependencias existentes ...

# Producción
gunicorn>=21.0.0
whitenoise>=6.5.0
dj-database-url>=2.0.0
python-decouple>=3.8
django-cors-headers>=4.0.0
psycopg2-binary>=2.9.0

# Seguridad
django-csp>=3.7
django-environ>=0.10.0
```

## 🏗️ Configuración de Producción

### 1. Configuraciones Django para Producción

Tu `settings.py` ya está bien configurado, pero añadiremos algunas mejoras:

#### Archivos Estáticos
```python
# En settings.py - añadir después de STATIC_URL
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Añadir WhiteNoise al middleware (después de SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Añadir esta línea
    # ... resto del middleware
]
```

### 2. Frontend - Configuración de Build

#### Archivo `frontend/.env.production`
```env
REACT_APP_API_URL=https://tudominio.com/api
REACT_APP_MAPBOX_TOKEN=tu_token_mapbox_aqui
GENERATE_SOURCEMAP=false
```

#### Comando de Build Optimizado
```json
// En frontend/package.json - añadir scripts
"scripts": {
    "build:prod": "REACT_APP_ENV=production npm run build",
    "analyze": "npm run build && npx serve -s build"
}
```

## 🌐 Opciones de Hosting

### Opción 1: VPS (Recomendado) - DigitalOcean, Linode, Vultr
**Costo**: $5-20/mes
**Ventajas**: Control total, escalable, mejor rendimiento
**Desventajas**: Requiere más configuración

### Opción 2: PaaS - Heroku, Railway, Render
**Costo**: $7-25/mes (con DB)
**Ventajas**: Deployment automático, menos configuración
**Desventajas**: Menos control, más caro a largo plazo

### Opción 3: Hosting Compartido + Netlify/Vercel
**Costo**: $3-10/mes
**Ventajas**: Muy económico
**Desventajas**: Limitaciones de Django

## 🚀 Deployment Paso a Paso (VPS con Ubuntu)

### 1. Preparar el Servidor

```bash
# Conectar al servidor
ssh root@tu_ip_servidor

# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias
apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor git -y

# Crear usuario para la aplicación
adduser blogapp
usermod -aG sudo blogapp
su - blogapp
```

### 2. Configurar Base de Datos PostgreSQL

```bash
# Como root
sudo -u postgres psql

-- En PostgreSQL
CREATE DATABASE travel_blog_db;
CREATE USER travel_blog_user WITH PASSWORD 'tu_password_segura';
ALTER ROLE travel_blog_user SET client_encoding TO 'utf8';
ALTER ROLE travel_blog_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE travel_blog_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE travel_blog_db TO travel_blog_user;
\q
```

### 3. Subir y Configurar el Código

```bash
# Como blogapp user
cd /home/blogapp
git clone https://github.com/tu_usuario/tu_repositorio.git blog
cd blog

# Configurar backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear archivo .env de producción
cp .env.development .env.production
nano .env.production
# (Editar con los valores de producción)

# Migrar base de datos
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Configurar frontend
cd ../frontend
npm install
npm run build
```

### 4. Configurar Nginx

```bash
# Crear configuración de Nginx
sudo nano /etc/nginx/sites-available/blog
```

```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    # Frontend estático
    location / {
        root /home/blogapp/blog/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Configurar Gunicorn con Supervisor

```bash
# Crear configuración de Supervisor
sudo nano /etc/supervisor/conf.d/blog.conf
```

```ini
[program:blog_gunicorn]
command=/home/blogapp/blog/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 core_project.wsgi:application
directory=/home/blogapp/blog/backend
user=blogapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/blog_gunicorn.log
environment=DJANGO_SETTINGS_MODULE=core_project.settings
```

```bash
# Activar configuración
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start blog_gunicorn
sudo supervisorctl status
```

### 6. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

## 🌍 Configuración de Dominio

### 1. Comprar Dominio
- **Recomendados**: Namecheap, GoDaddy, Google Domains
- **Costo**: $10-15/año

### 2. Configurar DNS
En tu proveedor de dominio, configurar:

```
Tipo    Nombre    Valor
A       @         IP_DE_TU_SERVIDOR
A       www       IP_DE_TU_SERVIDOR
CNAME   www       tudominio.com
```

## 📱 Scripts de Deployment Automatizado

### Script de Deployment (`deploy.sh`)
```bash
#!/bin/bash

echo "🚀 Iniciando deployment..."

# Backend
cd backend
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Frontend
cd ../frontend
npm install
npm run build

# Reiniciar servicios
sudo supervisorctl restart blog_gunicorn
sudo systemctl reload nginx

echo "✅ Deployment completado!"
```

### Script de Backup (`backup.sh`)
```bash
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/blogapp/backups"

mkdir -p $BACKUP_DIR

# Backup base de datos
pg_dump -h localhost -U travel_blog_user travel_blog_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup archivos media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/blogapp/blog/media/

echo "✅ Backup completado: $DATE"
```

## 📊 Monitoreo y Mantenimiento

### 1. Logs Importantes
```bash
# Logs de aplicación
sudo tail -f /var/log/supervisor/blog_gunicorn.log

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs de sistema
sudo journalctl -u nginx -f
```

### 2. Comandos de Mantenimiento
```bash
# Verificar estado de servicios
sudo systemctl status nginx
sudo supervisorctl status

# Reiniciar aplicación
sudo supervisorctl restart blog_gunicorn

# Ver espacio en disco
df -h

# Ver uso de memoria
free -h
```

### 3. Actualizaciones de Seguridad
```bash
# Ejecutar semanalmente
sudo apt update && sudo apt upgrade -y
sudo certbot renew
```

## 💡 Consejos Finales

1. **Backup Regular**: Configura backups automáticos diarios
2. **Monitoreo**: Usa herramientas como UptimeRobot para monitorear disponibilidad
3. **CDN**: Considera usar Cloudflare para mejor rendimiento
4. **Optimización**: Comprime imágenes antes de subirlas
5. **SEO**: Añade meta tags y sitemap.xml

## 🆘 Solución de Problemas Comunes

### Error 502 Bad Gateway
```bash
# Verificar que Gunicorn está corriendo
sudo supervisorctl status blog_gunicorn

# Reiniciar si es necesario
sudo supervisorctl restart blog_gunicorn
```

### Problemas con archivos estáticos
```bash
cd /home/blogapp/blog/backend
source venv/bin/activate
python manage.py collectstatic --clear --noinput
```

### Problemas de permisos en media
```bash
sudo chown -R blogapp:blogapp /home/blogapp/blog/media/
sudo chmod -R 755 /home/blogapp/blog/media/
```

---

¿Necesitas ayuda con algún paso específico? ¡Pregúntame y te ayudo a configurarlo paso a paso! 