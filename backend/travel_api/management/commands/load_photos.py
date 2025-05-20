import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from datetime import datetime
import pathlib
import json
import time
import requests
import uuid
from io import BytesIO

from travel_api.models import Lugar, Fotografia

THUMBNAIL_SIZE = (150, 150)

class Command(BaseCommand):
    help = 'Carga las fotos del directorio photos/ en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Forzar la carga de las fotos aunque ya existan')
        parser.add_argument('--limit', type=int, help='Limitar el número de fotos a cargar')

    def handle(self, *args, **options):
        force = options.get('force', False)
        limit = options.get('limit')
        
        if force:
            self.stdout.write(self.style.WARNING('Se ha especificado --force, se sobreescribirán las fotos existentes'))
        
        # Ruta a directorio de fotos - ajustar si es necesario
        photos_dir = os.path.join(os.getcwd(), '..', 'photos')
        if not os.path.isdir(photos_dir):
            photos_dir = os.path.join(os.getcwd(), 'photos')
        
        if not os.path.isdir(photos_dir):
            self.stdout.write(self.style.ERROR(f'No se encuentra el directorio de fotos en: {photos_dir}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Usando directorio de fotos: {photos_dir}'))
        
        # Crear directorio para miniaturas si no existe
        thumbnails_dir = os.path.join(photos_dir, 'thumbnails')
        if not os.path.isdir(thumbnails_dir):
            os.makedirs(thumbnails_dir)
            self.stdout.write(self.style.SUCCESS(f'Creado directorio para miniaturas: {thumbnails_dir}'))
        
        # Obtener lista de archivos en el directorio
        files = [f for f in os.listdir(photos_dir) if os.path.isfile(os.path.join(photos_dir, f)) 
                and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if limit:
            files = files[:limit]
            self.stdout.write(self.style.WARNING(f'Limitando a {limit} fotos'))
        
        total_fotos = len(files)
        self.stdout.write(self.style.SUCCESS(f'Se han encontrado {total_fotos} fotos'))
        
        # Procesar cada archivo
        for idx, file in enumerate(files, 1):
            try:
                file_path = os.path.join(photos_dir, file)
                self.stdout.write(f'Procesando {idx}/{total_fotos}: {file}')
                
                # Verificar si la foto ya existe
                if not force and Fotografia.objects.filter(nombre_archivo=file).exists():
                    self.stdout.write(self.style.WARNING(f'La foto {file} ya existe en la base de datos, saltando...'))
                    continue
                
                # Leer metadatos EXIF
                with open(file_path, 'rb') as img_file:
                    tags = exifread.process_file(img_file)
                
                # Extraer información de GPS
                gps_info = {}
                for tag, value in tags.items():
                    if tag.startswith('GPS'):
                        gps_info[tag] = str(value)
                
                # Intentar obtener coordenadas GPS de metadatos
                latitud = None
                longitud = None
                direccion = None
                
                # Comprobar si tenemos datos de GPS
                if 'GPS GPSLatitude' in gps_info and 'GPS GPSLongitude' in gps_info:
                    lat_ref = gps_info.get('GPS GPSLatitudeRef', 'N')
                    lon_ref = gps_info.get('GPS GPSLongitudeRef', 'E')
                    
                    # Convertir coordenadas a formato decimal
                    lat = self._convert_to_decimal(tags['GPS GPSLatitude'].values)
                    lon = self._convert_to_decimal(tags['GPS GPSLongitude'].values)
                    
                    # Ajustar signo según referencia
                    if lat_ref == 'S':
                        lat = -lat
                    if lon_ref == 'W':
                        lon = -lon
                    
                    latitud = lat
                    longitud = lon
                    
                    # Intentar geocodificación inversa para obtener dirección
                    try:
                        direccion = self._reverse_geocode(lat, lon)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error al geocodificar: {str(e)}'))
                
                # Guardar metadatos en archivo JSON
                metadata_file = os.path.join(photos_dir, os.path.splitext(file)[0] + '_metadata.json')
                with open(metadata_file, 'w') as f:
                    json.dump({
                        'file': file,
                        'exif': {k: str(v) for k, v in tags.items()},
                        'gps': gps_info,
                        'latitude': latitud,
                        'longitude': longitud,
                        'address': direccion
                    }, f, indent=2)
                
                # Crear o recuperar el Lugar
                if latitud and longitud and direccion:
                    # Extraer componentes de la dirección
                    ciudad = None
                    pais = None
                    nombre_lugar = None
                    
                    for component in direccion.get('components', {}):
                        if 'city' in component or 'town' in component or 'village' in component:
                            ciudad = component.get('city') or component.get('town') or component.get('village')
                        if 'country' in component:
                            pais = component.get('country')
                        if 'neighbourhood' in component or 'suburb' in component or 'road' in component:
                            nombre_lugar = (component.get('neighbourhood') or component.get('suburb') or 
                                          component.get('road') or component.get('formatted', '').split(',')[0])
                    
                    if not nombre_lugar:
                        nombre_lugar = direccion.get('formatted', '').split(',')[0] if 'formatted' in direccion else 'Lugar sin nombre'
                    
                    if not ciudad:
                        ciudad = 'Ciudad desconocida'
                    
                    if not pais:
                        pais = 'País desconocido'
                    
                    # Intentar encontrar un lugar existente cercano
                    lugar = None
                    lugares_cercanos = Lugar.objects.filter(
                        latitud__range=(latitud - 0.01, latitud + 0.01),
                        longitud__range=(longitud - 0.01, longitud + 0.01)
                    )
                    
                    if lugares_cercanos.exists():
                        lugar = lugares_cercanos.first()
                        self.stdout.write(self.style.SUCCESS(f'Usando lugar existente: {lugar.nombre}'))
                    else:
                        # Crear nuevo lugar
                        lugar = Lugar.objects.create(
                            nombre=nombre_lugar,
                            ciudad=ciudad,
                            pais=pais,
                            latitud=latitud,
                            longitud=longitud
                        )
                        self.stdout.write(self.style.SUCCESS(f'Creado nuevo lugar: {lugar.nombre}'))
                
                # Crear miniatura
                thumbnail_path = os.path.join('photos/thumbnails', os.path.splitext(file)[0] + '_thumb.jpeg')
                full_thumbnail_path = os.path.join(thumbnails_dir, os.path.splitext(file)[0] + '_thumb.jpeg')
                
                # Verificar si ya existe la miniatura
                if not os.path.exists(full_thumbnail_path) or force:
                    img = Image.open(file_path)
                    img.thumbnail(THUMBNAIL_SIZE)
                    img.save(full_thumbnail_path, 'JPEG')
                    self.stdout.write(self.style.SUCCESS(f'Creada miniatura: {thumbnail_path}'))
                
                # Fecha de toma de la foto
                fecha_toma = None
                if 'EXIF DateTimeOriginal' in tags:
                    try:
                        fecha_str = str(tags['EXIF DateTimeOriginal'])
                        fecha_toma = datetime.strptime(fecha_str, '%Y:%m:%d %H:%M:%S')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error al procesar fecha: {str(e)}'))
                
                # Crear o actualizar la fotografía en la base de datos
                if lugar:
                    # Generar UUID único si no existe
                    foto_uuid = str(uuid.uuid4())
                    
                    foto, created = Fotografia.objects.update_or_create(
                        nombre_archivo=file,
                        defaults={
                            'lugar': lugar,
                            'url_imagen': os.path.join('photos', file),
                            'thumbnail_url': thumbnail_path,
                            'uuid': foto_uuid,
                            'latitud_foto': latitud,
                            'longitud_foto': longitud,
                            'fecha_toma': fecha_toma,
                            'direccion_captura': direccion.get('formatted') if direccion and 'formatted' in direccion else None,
                            'es_foto_principal_lugar': not Fotografia.objects.filter(lugar=lugar, es_foto_principal_lugar=True).exists()
                        }
                    )
                    
                    action = 'Creada' if created else 'Actualizada'
                    self.stdout.write(self.style.SUCCESS(f'{action} fotografía en la base de datos: {file}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No se pudo determinar el lugar para la foto: {file}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al procesar {file}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Proceso de carga de fotos completado'))
        
        # Imprimir estadísticas
        total_lugares = Lugar.objects.count()
        total_fotos_bd = Fotografia.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total de lugares en la base de datos: {total_lugares}'))
        self.stdout.write(self.style.SUCCESS(f'Total de fotografías en la base de datos: {total_fotos_bd}'))
        
        # Verificar y corregir miniaturas faltantes
        fotos_sin_miniatura = Fotografia.objects.filter(thumbnail_url__isnull=True)
        if fotos_sin_miniatura.exists():
            self.stdout.write(self.style.WARNING(f'Hay {fotos_sin_miniatura.count()} fotos sin miniatura. Corrigiendo...'))
            for foto in fotos_sin_miniatura:
                if foto.url_imagen:
                    try:
                        file_name = os.path.basename(foto.url_imagen)
                        file_path = os.path.join(photos_dir, file_name)
                        
                        if os.path.exists(file_path):
                            thumbnail_path = os.path.join('photos/thumbnails', os.path.splitext(file_name)[0] + '_thumb.jpeg')
                            full_thumbnail_path = os.path.join(thumbnails_dir, os.path.splitext(file_name)[0] + '_thumb.jpeg')
                            
                            if not os.path.exists(full_thumbnail_path):
                                img = Image.open(file_path)
                                img.thumbnail(THUMBNAIL_SIZE)
                                img.save(full_thumbnail_path, 'JPEG')
                            
                            foto.thumbnail_url = thumbnail_path
                            foto.save()
                            self.stdout.write(self.style.SUCCESS(f'Corregida miniatura para: {file_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al corregir miniatura: {str(e)}'))
        
        # Todo correcto
        return

    def _convert_to_decimal(self, values):
        """Convierte coordenadas EXIF a formato decimal"""
        d = float(values[0].num) / float(values[0].den)
        m = float(values[1].num) / float(values[1].den)
        s = float(values[2].num) / float(values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    
    def _reverse_geocode(self, lat, lon):
        """Realiza geocodificación inversa para obtener la dirección"""
        # Utilizamos OpenCage Data API (puedes reemplazar por otra API si prefieres)
        api_key = 'ceb5e8bee5c7467b83d65ad7b9c2bfcf'  # Reemplaza por tu propia clave de API
        url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={api_key}'
        
        # Esperar brevemente para no exceder límites de la API
        time.sleep(1)
        
        response = requests.get(url)
        data = response.json()
        
        if data['status']['code'] == 200 and len(data['results']) > 0:
            return data['results'][0]
        else:
            raise Exception(f"No se pudo geocodificar: {data['status']['message']}") 