import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path

from travel_api.models import EntradaDeBlog, Fotografia

class Command(BaseCommand):
    help = """
    Elimina todas las fotos de una entrada de blog específica.
    
    Uso:
    python manage.py delete_blog_photos --blog-entry-id 6
    python manage.py delete_blog_photos --blog-title "Parque Nacional Natural Tayrona: El paraíso en la Tierra."
    python manage.py delete_blog_photos --blog-title "Mi Viaje" --delete-files
    """

    def add_arguments(self, parser):
        # Opciones para identificar la entrada
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--blog-entry-id',
            type=int,
            help='ID de la entrada de blog'
        )
        
        group.add_argument(
            '--blog-title',
            type=str,
            help='Título de la entrada de blog'
        )
        
        # Opciones de eliminación
        parser.add_argument(
            '--delete-files',
            action='store_true',
            help='Eliminar también los archivos físicos de fotos y thumbnails'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='No pedir confirmación antes de eliminar'
        )

    def handle(self, *args, **options):
        # Encontrar la entrada de blog
        entrada_blog = self._get_blog_entry(options)
        
        if not entrada_blog:
            raise CommandError("No se encontró la entrada de blog especificada")
        
        self.stdout.write(f"📝 Entrada encontrada: {entrada_blog.titulo} (ID: {entrada_blog.id})")
        
        # Obtener todas las fotos de esta entrada
        fotos = Fotografia.objects.filter(entrada_blog=entrada_blog)
        
        if not fotos.exists():
            self.stdout.write(self.style.WARNING("🔍 No se encontraron fotos en esta entrada de blog"))
            return
        
        total_fotos = fotos.count()
        self.stdout.write(f"📸 Se encontraron {total_fotos} fotos:")
        
        # Mostrar lista de fotos
        for i, foto in enumerate(fotos, 1):
            archivo = foto.url_imagen.split('/')[-1] if foto.url_imagen else 'Sin archivo'
            self.stdout.write(f"  {i}. ID {foto.id}: {archivo} (Orden: {foto.orden_en_entrada})")
        
        # Pedir confirmación si no se usa --force
        if not options['force']:
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.WARNING("⚠️  ¡ATENCIÓN! Esta acción eliminará TODAS las fotos listadas"))
            if options['delete_files']:
                self.stdout.write(self.style.WARNING("⚠️  También se eliminarán los archivos físicos"))
            self.stdout.write("="*60)
            
            confirm = input("\n¿Estás seguro de que quieres continuar? (escriba 'SI' para confirmar): ")
            
            if confirm != 'SI':
                self.stdout.write(self.style.ERROR("❌ Operación cancelada"))
                return
        
        # Proceder con la eliminación
        self.stdout.write(f"\n🗑️  Iniciando eliminación de {total_fotos} fotos...")
        
        archivos_eliminados = 0
        archivos_no_encontrados = 0
        errores_archivos = 0
        
        # Recopilar información de archivos antes de eliminar de la DB
        archivos_a_eliminar = []
        if options['delete_files']:
            for foto in fotos:
                if foto.url_imagen:
                    # Construir ruta completa del archivo
                    if foto.url_imagen.startswith('photos/'):
                        archivo_path = Path(settings.MEDIA_ROOT) / foto.url_imagen
                    else:
                        archivo_path = Path(foto.url_imagen)
                    
                    archivos_a_eliminar.append(archivo_path)
                
                if foto.thumbnail_url:
                    # Construir ruta completa del thumbnail
                    if foto.thumbnail_url.startswith('photos/'):
                        thumbnail_path = Path(settings.MEDIA_ROOT) / foto.thumbnail_url
                    else:
                        thumbnail_path = Path(foto.thumbnail_url)
                    
                    archivos_a_eliminar.append(thumbnail_path)
        
        # Eliminar registros de la base de datos
        fotos_eliminadas = fotos.delete()
        self.stdout.write(f"✅ Eliminados {fotos_eliminadas[0]} registros de la base de datos")
        
        # Eliminar archivos físicos si se solicita
        if options['delete_files'] and archivos_a_eliminar:
            self.stdout.write(f"\n🗂️  Eliminando {len(archivos_a_eliminar)} archivos físicos...")
            
            for archivo_path in archivos_a_eliminar:
                try:
                    if archivo_path.exists():
                        archivo_path.unlink()
                        archivos_eliminados += 1
                        self.stdout.write(f"  ✅ Eliminado: {archivo_path.name}")
                    else:
                        archivos_no_encontrados += 1
                        self.stdout.write(f"  ⚠️  No encontrado: {archivo_path.name}")
                except Exception as e:
                    errores_archivos += 1
                    self.stdout.write(f"  ❌ Error eliminando {archivo_path.name}: {str(e)}")
        
        # Resumen final
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"🎉 ELIMINACIÓN COMPLETADA")
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"📝 Entrada: {entrada_blog.titulo}")
        self.stdout.write(f"🗑️  Registros eliminados: {fotos_eliminadas[0]}")
        
        if options['delete_files']:
            self.stdout.write(f"📁 Archivos eliminados: {archivos_eliminados}")
            self.stdout.write(f"⚠️  Archivos no encontrados: {archivos_no_encontrados}")
            self.stdout.write(f"❌ Errores en archivos: {errores_archivos}")
        else:
            self.stdout.write(f"📁 Archivos físicos: No eliminados (usar --delete-files para eliminarlos)")
        
        # Enlaces útiles
        self.stdout.write(f"\n🔗 Enlaces útiles:")
        self.stdout.write(f"   Admin: http://localhost:8000/admin/travel_api/entradadeblog/{entrada_blog.id}/change/")
        self.stdout.write(f"   API: http://localhost:8000/api/entradas-blog/{entrada_blog.id}/")

    def _get_blog_entry(self, options):
        """Obtiene la entrada de blog según las opciones"""
        
        if options['blog_entry_id']:
            try:
                return EntradaDeBlog.objects.get(id=options['blog_entry_id'])
            except EntradaDeBlog.DoesNotExist:
                raise CommandError(f"No existe entrada de blog con ID {options['blog_entry_id']}")
        
        elif options['blog_title']:
            entrada = EntradaDeBlog.objects.filter(titulo=options['blog_title']).first()
            if not entrada:
                raise CommandError(f"No existe entrada de blog con título '{options['blog_title']}'")
            return entrada
        
        return None 