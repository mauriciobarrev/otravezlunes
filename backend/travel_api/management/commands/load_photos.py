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
import exifread
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
                if not force and Fotografia.objects.filter(url_imagen__contains=file).exists():
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
                        # Nota: Hacemos un intento de geocodificación, pero no es crítico si falla
                        direccion = self._reverse_geocode(lat, lon)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error al geocodificar: {str(e)}'))
                        # Si falla, proporcionamos un diccionario básico para no romper el flujo
                        direccion = {
                            'formatted': f'Ubicación en coordenadas: {lat:.6f}, {lon:.6f}',
                            'components': {}
                        }
                
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
                
                # Crear lugar si tenemos coordenadas
                lugar = None
                if latitud and longitud:
                    # Valores por defecto si no tenemos información de dirección
                    ciudad = "Ciudad desconocida"
                    pais = "País desconocido"
                    nombre_lugar = f"Lugar en {latitud:.6f}, {longitud:.6f}"
                    
                    # Intentar extraer componentes de la dirección si existe
                    if direccion and 'components' in direccion:
                        componentes = direccion['components']
                        # Nominatim devuelve un diccionario con claves directas
                        ciudad = (
                            componentes.get('city') or 
                            componentes.get('town') or 
                            componentes.get('village') or 
                            componentes.get('municipality') or
                            "Ciudad desconocida"
                        )
                        
                        pais = componentes.get('country', "País desconocido")
                        
                        nombre_lugar = (
                            componentes.get('road') or 
                            componentes.get('neighbourhood') or 
                            componentes.get('suburb') or
                            componentes.get('attraction') or
                            componentes.get('tourism') or
                            'Lugar sin nombre'
                        )
                    
                    # Si tenemos formatted, usar parte como nombre del lugar
                    if direccion and 'formatted' in direccion:
                        partes = direccion['formatted'].split(',')
                        if partes:
                            nombre_lugar = partes[0].strip()
                    
                    # Intentar encontrar un lugar existente cercano
                    lugares_cercanos = Lugar.objects.filter(
                        latitud__range=(latitud - 0.001, latitud + 0.001),
                        longitud__range=(longitud - 0.001, longitud + 0.001)
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
                            longitud=longitud,
                            descripcion_corta=f"Ubicación generada automáticamente en {ciudad}, {pais}" if ciudad and pais else "Ubicación generada automáticamente"
                        )
                        self.stdout.write(self.style.SUCCESS(f'Creado nuevo lugar: {lugar.nombre}'))
                else:
                    # Si no tenemos coordenadas, usar un lugar predeterminado o crear uno básico
                    self.stdout.write(self.style.WARNING('No se pudieron determinar coordenadas GPS para esta foto'))
                    lugar_default = Lugar.objects.filter(nombre='Lugar sin coordenadas GPS').first()
                    if lugar_default:
                        lugar = lugar_default
                    else:
                        lugar = Lugar.objects.create(
                            nombre='Lugar sin coordenadas GPS',
                            ciudad='Ciudad desconocida',
                            pais='País desconocido',
                            latitud=0,
                            longitud=0,
                            descripcion_corta='Lugar para fotos sin información de geolocalización'
                        )
                        self.stdout.write(self.style.SUCCESS('Creado lugar predeterminado para fotos sin GPS'))
                
                # Crear o actualizar la fotografía en la base de datos
                foto_uuid = str(uuid.uuid4())
                foto, created = Fotografia.objects.update_or_create(
                    url_imagen=os.path.join('photos', file),
                    defaults={
                        'lugar': lugar,
                        'uuid': foto_uuid,
                        'thumbnail_url': thumbnail_path,
                        'fecha_toma': fecha_toma,
                        'direccion_captura': direccion.get('formatted') if direccion and 'formatted' in direccion else None,
                        'descripcion': f"Fotografía en {lugar.nombre}",
                        'es_foto_principal_lugar': not Fotografia.objects.filter(lugar=lugar, es_foto_principal_lugar=True).exists()
                    }
                )
                
                action = 'Creada' if created else 'Actualizada'
                self.stdout.write(self.style.SUCCESS(f'{action} fotografía en la base de datos: {file}'))
                
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
        """
        Realiza geocodificación inversa usando Nominatim (OpenStreetMap)
        para obtener información de ubicación.
        """
        try:
            # Inicializar el geocodificador de Nominatim
            geolocator = Nominatim(user_agent="travel_blog_app")
            
            # Esperar brevemente para cumplir con los términos de servicio de Nominatim
            time.sleep(1)
            
            # Realizar la geocodificación inversa
            location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, language="es")
            
            if location and location.raw:
                # Formatear los resultados para mantener consistencia
                address = location.raw.get('address', {})
                formatted_address = location.address
                
                # Crear un diccionario similar al que usábamos antes
                return {
                    'formatted': formatted_address,
                    'components': address
                }
            
            # Si no hay resultados, devolver información básica
            return {
                'formatted': f'Ubicación en {lat:.6f}, {lon:.6f}',
                'components': {}
            }
        except Exception as e:
            # En caso de error, devolver información básica
            self.stdout.write(self.style.WARNING(f'Error en geocodificación con Nominatim: {str(e)}'))
            return {
                'formatted': f'Ubicación en {lat:.6f}, {lon:.6f}',
                'components': {}
            } 