import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from PIL import Image, ExifTags
import json
from datetime import datetime
import uuid
from pathlib import Path
import shutil

from travel_api.models import Lugar, EntradaDeBlog, Fotografia
from travel_api.utils import create_thumbnail

# Intentar importar exifread para mejor extracción de metadatos
try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

class Command(BaseCommand):
    help = """
    Carga fotos de una carpeta específica para una entrada de blog.
    
    Uso:
    python manage.py upload_blog_photos --source-folder "/ruta/a/las/fotos" --blog-entry-id 1
    python manage.py upload_blog_photos --source-folder "/Users/mauro/Fotos/Santiago_Chile" --blog-title "Mi Aventura en Santiago"
    python manage.py upload_blog_photos --source-folder "./fotos_temp/Madrid_2024" --create-blog --place-name "Madrid" --blog-title "Descubriendo Madrid"
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-folder',
            type=str,
            required=True,
            help='Ruta a la carpeta que contiene las fotos a cargar'
        )
        
        # Opciones para entrada existente
        parser.add_argument(
            '--blog-entry-id',
            type=int,
            help='ID de la entrada de blog existente'
        )
        
        parser.add_argument(
            '--blog-title',
            type=str,
            help='Título de la entrada de blog (busca por título o crea nueva si se usa con --create-blog)'
        )
        
        # Opciones para crear nueva entrada
        parser.add_argument(
            '--create-blog',
            action='store_true',
            help='Crear nueva entrada de blog si no existe'
        )
        
        parser.add_argument(
            '--place-name',
            type=str,
            help='Nombre del lugar (necesario si se crea nueva entrada)'
        )
        
        parser.add_argument(
            '--place-coords',
            type=str,
            help='Coordenadas del lugar en formato "lat,lng" (ej: "-33.4485,-70.6693")'
        )
        
        parser.add_argument(
            '--description',
            type=str,
            help='Descripción para la entrada de blog'
        )
        
        # Opciones de procesamiento
        parser.add_argument(
            '--force-overwrite',
            action='store_true',
            help='Sobrescribir fotos existentes'
        )
        
        parser.add_argument(
            '--copy-to-media',
            action='store_true',
            default=True,
            help='Copiar archivos a la carpeta media (por defecto: True)'
        )
        
        parser.add_argument(
            '--supported-extensions',
            type=str,
            default='jpg,jpeg,png,tiff,raw',
            help='Extensiones de archivo soportadas (separadas por comas)'
        )

    def handle(self, *args, **options):
        # Validar carpeta fuente
        source_folder = Path(options['source_folder']).expanduser().resolve()
        if not source_folder.exists() or not source_folder.is_dir():
            raise CommandError(f"La carpeta '{source_folder}' no existe o no es un directorio")
        
        self.stdout.write(f"📁 Carpeta fuente: {source_folder}")
        
        # Buscar archivos de imagen
        extensions = [ext.strip().lower() for ext in options['supported_extensions'].split(',')]
        image_files = []
        
        for ext in extensions:
            image_files.extend(source_folder.glob(f"*.{ext}"))
            image_files.extend(source_folder.glob(f"*.{ext.upper()}"))
        
        if not image_files:
            raise CommandError(f"No se encontraron imágenes en {source_folder} con extensiones: {extensions}")
        
        self.stdout.write(f"🖼️  Encontradas {len(image_files)} imágenes")
        
        # Determinar entrada de blog
        entrada_blog = self._get_or_create_blog_entry(options)
        self.stdout.write(f"📝 Entrada de blog: {entrada_blog.titulo} (ID: {entrada_blog.id})")
        
        # Procesar cada imagen
        fotos_creadas = 0
        fotos_saltadas = 0
        errores = 0
        
        for orden, image_file in enumerate(sorted(image_files), start=1):
            try:
                self.stdout.write(f"\n📸 Procesando [{orden}/{len(image_files)}]: {image_file.name}")
                
                # Verificar si ya existe
                if not options['force_overwrite']:
                    if Fotografia.objects.filter(
                        entrada_blog=entrada_blog,
                        url_imagen__contains=image_file.name
                    ).exists():
                        self.stdout.write(f"  ⏩ Ya existe, saltando...")
                        fotos_saltadas += 1
                        continue
                
                # Crear fotografía
                foto = self._create_fotografia(
                    image_file, 
                    entrada_blog, 
                    orden, 
                    options['copy_to_media']
                )
                
                if foto:
                    fotos_creadas += 1
                    self.stdout.write(f"  ✅ Creada foto ID {foto.id}")
                else:
                    errores += 1
                    
            except Exception as e:
                self.stdout.write(f"  ❌ Error: {str(e)}")
                errores += 1
        
        # Resumen final
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"🎉 CARGA COMPLETADA")
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"✅ Fotos creadas: {fotos_creadas}")
        self.stdout.write(f"⏩ Fotos saltadas: {fotos_saltadas}")
        self.stdout.write(f"❌ Errores: {errores}")
        self.stdout.write(f"📝 Entrada de blog: {entrada_blog.titulo}")
        self.stdout.write(f"🌍 Lugar: {entrada_blog.lugar_asociado.nombre if entrada_blog.lugar_asociado else 'Sin lugar asociado'}")
        
        # Enlaces útiles
        self.stdout.write(f"\n🔗 Enlaces útiles:")
        self.stdout.write(f"   Admin: http://localhost:8000/admin/travel_api/entradadeblog/{entrada_blog.id}/change/")
        self.stdout.write(f"   API: http://localhost:8000/api/entradas-blog/{entrada_blog.id}/")

    def _get_or_create_blog_entry(self, options):
        """Obtiene o crea una entrada de blog según las opciones"""
        
        # Opción 1: ID específico
        if options['blog_entry_id']:
            try:
                return EntradaDeBlog.objects.get(id=options['blog_entry_id'])
            except EntradaDeBlog.DoesNotExist:
                raise CommandError(f"No existe entrada de blog con ID {options['blog_entry_id']}")
        
        # Opción 2: Buscar por título
        if options['blog_title']:
            entrada = EntradaDeBlog.objects.filter(titulo=options['blog_title']).first()
            if entrada:
                return entrada
            
            # Si no existe, intentar crearla automáticamente
            self.stdout.write(f"⚠️  La entrada '{options['blog_title']}' no existe. Creando automáticamente...")
            if not options['place_name']:
                # Intentar inferir el nombre del lugar desde el título
                options['place_name'] = options['blog_title']
                self.stdout.write(f"📍 Usando '{options['place_name']}' como nombre del lugar")
            
            return self._create_blog_entry(options)
        
        # Si no se especifica nada
        raise CommandError("Debes especificar --blog-entry-id o --blog-title")

    def _create_blog_entry(self, options):
        """Crea una nueva entrada de blog"""
        
        if not options['blog_title']:
            raise CommandError("Se requiere --blog-title para crear una nueva entrada")
        
        # Obtener o crear lugar
        lugar = self._get_or_create_place(options)
        
        # Obtener usuario (el primero disponible)
        from django.contrib.auth.models import User
        usuario = User.objects.first()
        if not usuario:
            raise CommandError("No hay usuarios en el sistema. Crea un superusuario primero.")
        
        # Crear entrada de blog
        entrada = EntradaDeBlog.objects.create(
            titulo=options['blog_title'],
            descripcion=options.get('description', ''),
            lugar_asociado=lugar,
            autor=usuario,
            contenido_markdown=options.get('description', '') or f"# {options['blog_title']}\n\nEntrada de blog creada automáticamente."
        )
        
        self.stdout.write(f"✨ Nueva entrada de blog creada: {entrada.titulo}")
        return entrada

    def _get_or_create_place(self, options):
        """Obtiene o crea un lugar"""
        
        if not options['place_name']:
            raise CommandError("Se requiere --place-name para crear una nueva entrada de blog")
        
        # Buscar lugar existente
        lugar = Lugar.objects.filter(nombre=options['place_name']).first()
        if lugar:
            return lugar
        
        # Crear nuevo lugar
        lat, lng = -33.4485, -70.6693  # Santiago por defecto
        
        if options['place_coords']:
            try:
                coords = options['place_coords'].split(',')
                lat, lng = float(coords[0].strip()), float(coords[1].strip())
            except (ValueError, IndexError):
                self.stdout.write(f"⚠️  Coordenadas inválidas, usando Santiago por defecto")
        
        lugar = Lugar.objects.create(
            nombre=options['place_name'],
            ciudad=options['place_name'],  # Usar nombre como ciudad por defecto
            pais='Chile',  # País por defecto
            latitud=lat,
            longitud=lng,
            descripcion_corta=f"Lugar creado automáticamente para {options['place_name']}"
        )
        
        self.stdout.write(f"🌍 Nuevo lugar creado: {lugar.nombre}")
        return lugar

    def _create_fotografia(self, image_file, entrada_blog, orden, copy_to_media=True):
        """Crea un objeto Fotografia desde un archivo de imagen"""
        
        try:
            # Extraer metadatos EXIF
            metadata = self._extract_metadata(image_file)
            
            # Determinar nombre final del archivo
            filename = f"{uuid.uuid4().hex}_{image_file.name}"
            
            if copy_to_media:
                # Copiar archivo a media/photos/
                media_photos_dir = Path(settings.MEDIA_ROOT) / 'photos'
                media_photos_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = media_photos_dir / filename
                shutil.copy2(image_file, dest_path)
                
                # Crear thumbnail
                thumbnail_dir = media_photos_dir / 'thumbnails'
                thumbnail_dir.mkdir(parents=True, exist_ok=True)
                
                thumbnail_filename = f"{Path(filename).stem}_thumb{Path(filename).suffix}"
                self._create_thumbnail_file(dest_path, thumbnail_dir / thumbnail_filename)
                
                # URLs relativas
                imagen_url = f"photos/{filename}"
                thumbnail_url = f"photos/thumbnails/{thumbnail_filename}"
            else:
                # Usar archivo en ubicación original
                imagen_url = str(image_file)
                thumbnail_url = str(image_file)  # Por simplicidad
            
            # Crear objeto Fotografia
            foto = Fotografia.objects.create(
                lugar=entrada_blog.lugar_asociado,
                entrada_blog=entrada_blog,
                url_imagen=imagen_url,
                thumbnail_url=thumbnail_url,
                descripcion=metadata.get('description', f"Fotografía en {entrada_blog.lugar_asociado.nombre}"),
                autor_fotografia=metadata.get('author', 'mauribarrev'),
                fecha_toma=metadata.get('date_taken'),
                orden_en_entrada=orden,
                direccion_captura=metadata.get('location_description', '')
            )
            
            return foto
            
        except Exception as e:
            self.stdout.write(f"  ❌ Error creando fotografía: {str(e)}")
            return None

    def _extract_metadata(self, image_file):
        """Extrae metadatos de la imagen"""
        metadata = {
            'author': 'mauribarrev',  # Autor por defecto
            'description': image_file.stem.replace('_', ' ').replace('-', ' ').title()
        }
        
        # Intentar extraer fecha con exifread (más robusto)
        if EXIFREAD_AVAILABLE:
            try:
                with open(image_file, 'rb') as f:
                    tags = exifread.process_file(f)
                    
                    # Campos de fecha en orden de preferencia
                    date_fields = [
                        'EXIF DateTimeOriginal',
                        'EXIF DateTimeDigitized', 
                        'EXIF DateTime',
                        'Image DateTime'
                    ]
                    
                    for field in date_fields:
                        if field in tags:
                            try:
                                date_str = str(tags[field])
                                parsed_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                metadata['date_taken'] = parsed_date.date()
                                self.stdout.write(f"  📅 Fecha EXIF extraída: {metadata['date_taken']} ({field})")
                                break
                            except ValueError as e:
                                self.stdout.write(f"  ⚠️  Error parseando {field}: {date_str}")
                                continue
                                
            except Exception as e:
                self.stdout.write(f"  ⚠️  Error con exifread: {str(e)}")
        
        # Si no se extrajo con exifread, intentar con PIL
        if 'date_taken' not in metadata:
            try:
                with Image.open(image_file) as img:
                    exif = img._getexif()
                    if exif:
                        # Buscar fecha de toma en diferentes campos EXIF
                        date_fields = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
                        for tag, value in exif.items():
                            decoded = ExifTags.TAGS.get(tag, tag)
                            if decoded in date_fields:
                                try:
                                    parsed_date = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                                    metadata['date_taken'] = parsed_date.date()
                                    self.stdout.write(f"  📅 Fecha PIL extraída: {metadata['date_taken']} ({decoded})")
                                    break
                                except ValueError:
                                    continue
                                    
            except Exception as e:
                self.stdout.write(f"  ⚠️  Error con PIL EXIF: {str(e)}")
        
        # Como último recurso, usar fecha de modificación del archivo
        if 'date_taken' not in metadata:
            try:
                file_stat = image_file.stat()
                file_date = datetime.fromtimestamp(file_stat.st_mtime).date()
                metadata['date_taken'] = file_date
                self.stdout.write(f"  📅 Fecha de archivo: {metadata['date_taken']}")
            except Exception as e:
                self.stdout.write(f"  ⚠️  Error obteniendo fecha de archivo: {str(e)}")
        
        return metadata

    def _create_thumbnail_file(self, source_path, thumbnail_path):
        """Crea un archivo thumbnail"""
        try:
            with Image.open(source_path) as img:
                # Convertir a RGB si es necesario (para JPEGs)
                if img.mode in ('RGBA', 'LA'):
                    # Crear fondo blanco para imágenes con transparencia
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Crear thumbnail manteniendo proporción
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Guardar como JPEG con buena calidad
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                self.stdout.write(f"  📷 Thumbnail creado: {thumbnail_path.name}")
                
        except Exception as e:
            self.stdout.write(f"  ⚠️  Error creando thumbnail: {str(e)}")
            return False
        
        return True 