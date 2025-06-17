from django.core.management.base import BaseCommand
from travel_api.models import Fotografia
from travel_api.utils import create_thumbnail

class Command(BaseCommand):
    help = 'Genera thumbnails para todas las fotografías que no los tienen'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Buscando fotografías sin thumbnails...")
        
        # Buscar fotos que tienen imagen pero no thumbnail
        fotos_sin_thumbnail = Fotografia.objects.filter(
            imagen__isnull=False,
            thumbnail__isnull=True
        ) | Fotografia.objects.filter(
            imagen__isnull=False,
            thumbnail=''
        )
        
        self.stdout.write(f"📸 Encontradas {fotos_sin_thumbnail.count()} fotografías sin thumbnail")
        
        success_count = 0
        error_count = 0
        
        for foto in fotos_sin_thumbnail:
            try:
                self.stdout.write(f"📷 Procesando foto ID {foto.id}: {foto.descripcion or 'Sin descripción'}")
                
                # Crear thumbnail
                thumbnail_file = create_thumbnail(foto.imagen)
                
                if thumbnail_file:
                    # Guardar el thumbnail
                    foto.thumbnail.save(
                        thumbnail_file.name,
                        thumbnail_file,
                        save=False  # No activar signals
                    )
                    
                    # Actualizar URLs
                    foto.url_imagen = foto.imagen.url
                    foto.thumbnail_url = foto.thumbnail.url
                    foto.save()
                    
                    self.stdout.write(f"  ✅ Thumbnail generado: {foto.thumbnail.url}")
                    success_count += 1
                else:
                    self.stdout.write(f"  ❌ Error: No se pudo crear thumbnail")
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(f"  ❌ Error procesando foto ID {foto.id}: {str(e)}")
                error_count += 1
        
        # Resumen
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 RESUMEN")
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Thumbnails generados exitosamente: {success_count}")
        self.stdout.write(f"❌ Errores: {error_count}")
        self.stdout.write(f"📸 Total procesado: {success_count + error_count}")
        
        if success_count > 0:
            self.stdout.write("\n🎉 ¡Thumbnails generados! Puedes verlos en:")
            self.stdout.write("   📋 Admin: http://localhost:8000/admin/travel_api/fotografia/")
            self.stdout.write("   🌐 API: http://localhost:8000/api/fotografias/") 