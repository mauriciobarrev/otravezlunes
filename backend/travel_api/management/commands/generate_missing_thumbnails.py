import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image
from pathlib import Path
import logging

from travel_api.models import Fotografia

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
    Genera thumbnails para todas las fotografías que no los tienen o los tienen rotos.
    
    Uso:
    python manage.py generate_missing_thumbnails
    python manage.py generate_missing_thumbnails --force  # Regenerar todos
    python manage.py generate_missing_thumbnails --entrada-id 6  # Solo una entrada
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerar todos los thumbnails, incluso los que ya existen'
        )
        
        parser.add_argument(
            '--entrada-id',
            type=int,
            help='Solo procesar fotos de una entrada específica'
        )
        
        parser.add_argument(
            '--size',
            type=str,
            default='300x300',
            help='Tamaño del thumbnail en formato "WIDTHxHEIGHT" (default: 300x300)'
        )

    def handle(self, *args, **options):
        # Parsear tamaño
        try:
            width, height = map(int, options['size'].split('x'))
            thumbnail_size = (width, height)
        except:
            thumbnail_size = (300, 300)
            self.stdout.write(f"⚠️  Tamaño inválido, usando {thumbnail_size}")
        
        self.stdout.write(f"🖼️  Generando thumbnails de tamaño {thumbnail_size}")
        
        # Obtener fotografías a procesar
        queryset = Fotografia.objects.all()
        
        if options['entrada_id']:
            queryset = queryset.filter(entrada_blog_id=options['entrada_id'])
            self.stdout.write(f"📝 Procesando solo entrada ID {options['entrada_id']}")
        
        total_fotos = queryset.count()
        self.stdout.write(f"📸 Total de fotos a revisar: {total_fotos}")
        
        if total_fotos == 0:
            self.stdout.write("⚠️  No hay fotos para procesar")
            return
        
        # Contadores
        thumbnails_creados = 0
        thumbnails_regenerados = 0
        errores = 0
        sin_archivo = 0
        ya_existen = 0
        
        # Crear directorio de thumbnails si no existe
        thumbnail_base_dir = Path(settings.MEDIA_ROOT) / 'photos' / 'thumbnails'
        thumbnail_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Procesar cada foto
        for i, foto in enumerate(queryset, 1):
            try:
                self.stdout.write(f"\n📸 [{i}/{total_fotos}] ID {foto.id}: ", ending='')
                
                # Verificar que existe la imagen original
                if not foto.url_imagen:
                    self.stdout.write("❌ Sin URL de imagen")
                    sin_archivo += 1
                    continue
                
                # Construir ruta de la imagen original
                if foto.url_imagen.startswith('photos/'):
                    imagen_path = Path(settings.MEDIA_ROOT) / foto.url_imagen
                else:
                    imagen_path = Path(foto.url_imagen)
                
                if not imagen_path.exists():
                    self.stdout.write(f"❌ Archivo no encontrado: {imagen_path}")
                    sin_archivo += 1
                    continue
                
                # Determinar ruta del thumbnail
                filename = imagen_path.name
                thumbnail_filename = f"{imagen_path.stem}_thumb{imagen_path.suffix}"
                thumbnail_path = thumbnail_base_dir / thumbnail_filename
                thumbnail_url = f"photos/thumbnails/{thumbnail_filename}"
                
                # Verificar si ya existe el thumbnail
                thumbnail_exists = thumbnail_path.exists()
                
                if thumbnail_exists and not options['force']:
                    self.stdout.write("⏩ Ya existe")
                    ya_existen += 1
                    
                    # Actualizar URL en la base de datos si no está establecida
                    if not foto.thumbnail_url:
                        foto.thumbnail_url = thumbnail_url
                        foto.save(update_fields=['thumbnail_url'])
                        self.stdout.write(" (URL actualizada)")
                    
                    continue
                
                # Crear/regenerar thumbnail
                success = self._create_thumbnail(imagen_path, thumbnail_path, thumbnail_size)
                
                if success:
                    # Actualizar base de datos
                    foto.thumbnail_url = thumbnail_url
                    foto.save(update_fields=['thumbnail_url'])
                    
                    if thumbnail_exists:
                        self.stdout.write("🔄 Regenerado")
                        thumbnails_regenerados += 1
                    else:
                        self.stdout.write("✅ Creado")
                        thumbnails_creados += 1
                else:
                    errores += 1
                    
            except Exception as e:
                self.stdout.write(f"❌ Error: {str(e)}")
                errores += 1
        
        # Resumen final
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"🎉 GENERACIÓN DE THUMBNAILS COMPLETADA")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(f"📸 Total procesadas: {total_fotos}")
        self.stdout.write(f"✅ Thumbnails creados: {thumbnails_creados}")
        self.stdout.write(f"🔄 Thumbnails regenerados: {thumbnails_regenerados}")
        self.stdout.write(f"⏩ Ya existían: {ya_existen}")
        self.stdout.write(f"📁 Sin archivo original: {sin_archivo}")
        self.stdout.write(f"❌ Errores: {errores}")
        
        if thumbnails_creados > 0 or thumbnails_regenerados > 0:
            self.stdout.write(f"\n🔗 Revisa el admin:")
            self.stdout.write(f"   http://localhost:8000/admin/travel_api/fotografia/")

    def _create_thumbnail(self, source_path, thumbnail_path, size):
        """Crea un thumbnail de la imagen"""
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
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Guardar como JPEG con buena calidad
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                
                return True
                
        except Exception as e:
            self.stdout.write(f"❌ Error creando thumbnail: {str(e)}")
            return False 