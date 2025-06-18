# 📸 Guía de Carga de Fotos - Blog de Viajes

Esta guía te explica cómo cargar múltiples fotos de manera eficiente a tu blog de viajes.

## 🚀 Métodos de Carga

### Método 1: Script Simplificado (Recomendado)

Usa el script `upload_photos.py` desde la raíz del proyecto:

```bash
# Hacer el script ejecutable (solo una vez)
chmod +x upload_photos.py

# Cargar fotos a entrada existente
python upload_photos.py ~/Pictures/Santiago_Chile --blog "Mi Aventura en Santiago"

# Crear nueva entrada y cargar fotos
python upload_photos.py ./fotos_madrid --blog "Descubriendo Madrid" --new --place "Madrid"

# Con coordenadas específicas
python upload_photos.py ~/fotos/amsterdam --blog "Amsterdam Experience" --new --place "Amsterdam" --coords "52.3676,4.9041"
```

### Método 2: Comando Django Directo

Desde la carpeta `backend/`:

```bash
cd backend

# Cargar a entrada existente por ID
python manage.py upload_blog_photos --source-folder "/Users/mauro/Pictures/Viaje_Barcelona" --blog-entry-id 3

# Cargar a entrada existente por título
python manage.py upload_blog_photos --source-folder "~/fotos/roma" --blog-title "Roma Eterna"

# Crear nueva entrada automáticamente
python manage.py upload_blog_photos \
  --source-folder "./fotos_temp/Madrid_2024" \
  --create-blog \
  --place-name "Madrid" \
  --blog-title "Descubriendo Madrid" \
  --place-coords "40.4168,-3.7038" \
  --description "Mi increíble viaje por la capital española"
```

## 📋 Parámetros Disponibles

### Parámetros Principales
- `--source-folder` o `folder`: Carpeta que contiene las fotos (requerido)
- `--blog-entry-id` o `--id`: ID de entrada existente
- `--blog-title` o `--blog`: Título de la entrada de blog

### Para Crear Nueva Entrada
- `--create-blog` o `--new`: Permite crear nueva entrada si no existe
- `--place-name` o `--place`: Nombre del lugar (requerido para nuevas entradas)
- `--place-coords` o `--coords`: Coordenadas GPS en formato "lat,lng"
- `--description`: Descripción de la entrada de blog

### Opciones de Procesamiento
- `--force-overwrite` o `--force`: Sobrescribir fotos existentes
- `--supported-extensions`: Extensiones soportadas (default: jpg,jpeg,png,tiff,raw)
- `--copy-to-media`: Copiar archivos a carpeta media (default: True)

## 🗂️ Organización de Carpetas Recomendada

Organiza tus fotos siguiendo estos patrones:

```
~/Pictures/Viajes/
├── Santiago_Chile_2024/
│   ├── IMG_001.jpg
│   ├── IMG_002.jpg
│   └── catedral.jpg
├── Barcelona_Marzo_2024/
│   ├── sagrada_familia.jpg
│   ├── park_guell_01.jpg
│   └── ramblas.jpg
└── Amsterdam_Abril_2024/
    ├── canales_01.jpg
    ├── museo_van_gogh.jpg
    └── vondelpark.jpg
```

## 💡 Ejemplos Prácticos

### Escenario 1: Primera vez cargando fotos de Santiago

```bash
# Crear entrada nueva con lugar y coordenadas
python upload_photos.py ~/Pictures/Santiago_Chile_2024 \
  --blog "Mi Aventura en Santiago de Chile" \
  --new \
  --place "Santiago de Chile" \
  --coords "-33.4485,-70.6693" \
  --description "Explorando la hermosa capital chilena"
```

### Escenario 2: Agregar más fotos a una entrada existente

```bash
# Buscar por título de entrada existente
python upload_photos.py ~/Pictures/Mas_fotos_Santiago \
  --blog "Mi Aventura en Santiago de Chile"
```

### Escenario 3: Cargar fotos usando ID específico

```bash
# Si conoces el ID de la entrada (más rápido)
python upload_photos.py ~/Pictures/Barcelona_Adicionales \
  --id 5
```

### Escenario 4: Reemplazar fotos existentes

```bash
# Forzar sobreescritura de fotos que ya existen
python upload_photos.py ~/Pictures/Roma_Nuevas \
  --blog "Roma Eterna" \
  --force
```

## 🔧 Solución de Problemas

### Error: "No se encuentra manage.py"
```bash
# Asegúrate de estar en la raíz del proyecto
cd /Users/maurobarrev/Documents/Mau/projects/blog
python upload_photos.py [opciones]
```

### Error: "No hay usuarios en el sistema"
```bash
# Crear superusuario primero
cd backend
python manage.py createsuperuser
```

### Error: "La carpeta no existe"
```bash
# Verifica la ruta usando rutas absolutas
python upload_photos.py "/Users/mauro/Pictures/Viaje_Madrid" --blog "Madrid 2024" --new --place "Madrid"
```

### Ver fotos existentes
```bash
# Listar entradas de blog actuales
cd backend
python manage.py shell -c "
from travel_api.models import EntradaDeBlog
for e in EntradaDeBlog.objects.all():
    print(f'ID: {e.id} - {e.titulo} - Fotos: {e.fotografias.count()}')
"
```

## 📊 Después de la Carga

Una vez cargadas las fotos, puedes:

1. **Ver en el admin de Django**: `http://localhost:8000/admin/travel_api/entradadeblog/`
2. **Revisar la API**: `http://localhost:8000/api/entradas-blog/`
3. **Ver en el mapa**: Abrir el frontend y buscar los nuevos marcadores

## 🎯 Consejos de Uso

1. **Nombres descriptivos**: Usa nombres de carpeta descriptivos como `Madrid_Abril_2024` en lugar de `Fotos_001`

2. **Coordenadas precisas**: Busca las coordenadas en Google Maps para mejor ubicación en el mapa

3. **Orden de fotos**: Las fotos se ordenan alfabéticamente, usa prefijos numéricos si quieres un orden específico:
   ```
   01_llegada_aeropuerto.jpg
   02_hotel_vista.jpg
   03_primera_caminata.jpg
   ```

4. **Tamaño de archivos**: El script maneja automáticamente la creación de thumbnails, no necesitas redimensionar previamente

5. **Backup**: Siempre mantén una copia de seguridad de tus fotos originales antes de procesarlas

## 🚨 Advertencias

- ⚠️ El flag `--force` sobrescribirá fotos existentes sin preguntar
- ⚠️ Las coordenadas deben estar en formato decimal (ej: "40.4168,-3.7038")
- ⚠️ Los archivos RAW se copiarán pero pueden no mostrarse correctamente en el navegador 