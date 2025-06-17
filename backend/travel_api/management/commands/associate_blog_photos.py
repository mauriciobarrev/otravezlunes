from django.core.management.base import BaseCommand
from travel_api.models import Lugar, EntradaDeBlog, Fotografia
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Asocia la entrada de blog "Mi Aventura en Santiago de Chile" con las fotos de Calle Cerro Calderico'

    def handle(self, *args, **options):
        self.stdout.write("=== ESTADO ACTUAL ===")
        
        # Mostrar lugares existentes
        self.stdout.write("\n🏢 LUGARES:")
        for lugar in Lugar.objects.all():
            self.stdout.write(f"  ID: {lugar.id} - {lugar.nombre} ({lugar.ciudad}, {lugar.pais})")
        
        # Mostrar entradas de blog
        self.stdout.write("\n📝 ENTRADAS DE BLOG:")
        for entrada in EntradaDeBlog.objects.all():
            lugar_asociado = entrada.lugar_asociado.nombre if entrada.lugar_asociado else "Sin lugar"
            self.stdout.write(f"  ID: {entrada.id} - {entrada.titulo} (Asociado a: {lugar_asociado})")
        
        # Mostrar fotografías
        self.stdout.write("\n📸 FOTOGRAFÍAS:")
        for foto in Fotografia.objects.all():
            entrada_asociada = foto.entrada_blog.titulo if foto.entrada_blog else "Sin entrada de blog"
            self.stdout.write(f"  ID: {foto.id} - {foto.lugar.nombre} (Blog: {entrada_asociada})")
        
        # Buscar la entrada de blog "Mi Aventura en Santiago de Chile"
        try:
            entrada_santiago = EntradaDeBlog.objects.get(titulo="Mi Aventura en Santiago de Chile")
            self.stdout.write(f"\n✅ Encontrada entrada de blog: {entrada_santiago.titulo}")
        except EntradaDeBlog.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ No se encontró la entrada 'Mi Aventura en Santiago de Chile'"))
            return
        
        # Buscar o crear el lugar "Calle Cerro Calderico"
        lugar_calderico, created = Lugar.objects.get_or_create(
            nombre="Calle Cerro Calderico",
            defaults={
                'ciudad': 'Santiago',
                'pais': 'Chile',
                'latitud': -33.4485,  # Coordenadas aproximadas de Santiago
                'longitud': -70.6693,
                'descripcion_corta': 'Una pintoresca calle en Santiago con hermosas vistas y arquitectura tradicional.'
            }
        )
        
        if created:
            self.stdout.write(f"✅ Creado nuevo lugar: {lugar_calderico.nombre}")
        else:
            self.stdout.write(f"✅ Encontrado lugar existente: {lugar_calderico.nombre}")
        
        # Asociar la entrada de blog con el lugar
        if not entrada_santiago.lugar_asociado:
            entrada_santiago.lugar_asociado = lugar_calderico
            entrada_santiago.save()
            self.stdout.write(f"✅ Asociada entrada de blog con {lugar_calderico.nombre}")
        
        # Buscar fotos existentes que podrían ser de Calle Cerro Calderico
        # Primero, veamos si hay fotos que mencionen "Calderico" o están sin entrada de blog
        fotos_candidatas = Fotografia.objects.filter(
            entrada_blog__isnull=True
        ) | Fotografia.objects.filter(
            descripcion__icontains="Calderico"
        ) | Fotografia.objects.filter(
            descripcion__icontains="Santiago"
        )
        
        self.stdout.write(f"\n🔍 Encontradas {fotos_candidatas.count()} fotos candidatas para asociar:")
        
        if fotos_candidatas.exists():
            orden = 1
            for foto in fotos_candidatas:
                # Asociar la foto con la entrada de blog y el lugar
                foto.entrada_blog = entrada_santiago
                foto.lugar = lugar_calderico
                foto.orden_en_entrada = orden
                
                # Si la descripción está vacía, agregar una descripción por defecto
                if not foto.descripcion:
                    foto.descripcion = f"Fotografía en Calle Cerro Calderico, Santiago de Chile"
                
                foto.save()
                self.stdout.write(f"  ✅ Asociada foto ID {foto.id} (Orden: {orden})")
                orden += 1
        
        # Si no hay fotos candidatas, crear algunas fotos de ejemplo usando las imágenes existentes
        if not fotos_candidatas.exists():
            self.stdout.write("\n📁 No se encontraron fotos candidatas. Creando fotos de ejemplo...")
            
            # Buscar archivos en la carpeta photos
            import os
            from django.conf import settings
            
            photos_dir = os.path.join(settings.BASE_DIR.parent, 'photos')
            if os.path.exists(photos_dir):
                image_files = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                
                for i, filename in enumerate(image_files[:3], 1):  # Tomar máximo 3 fotos
                    foto = Fotografia.objects.create(
                        lugar=lugar_calderico,
                        entrada_blog=entrada_santiago,
                        url_imagen=f"photos/{filename}",
                        thumbnail_url=f"photos/thumbnails/{filename.replace('.', '_thumb.')}",
                        descripcion=f"Vista de Calle Cerro Calderico - Fotografía {i}",
                        orden_en_entrada=i,
                        fecha_toma="2025-03-07"
                    )
                    self.stdout.write(f"  ✅ Creada foto de ejemplo ID {foto.id}: {filename}")
        
        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write("✅ ASOCIACIÓN COMPLETADA")
        self.stdout.write("="*50)
        
        # Verificar el resultado
        fotos_asociadas = Fotografia.objects.filter(entrada_blog=entrada_santiago)
        self.stdout.write(f"📸 Total de fotos asociadas a '{entrada_santiago.titulo}': {fotos_asociadas.count()}")
        
        for foto in fotos_asociadas:
            self.stdout.write(f"  - Foto ID {foto.id}: {foto.descripcion or 'Sin descripción'} (Orden: {foto.orden_en_entrada})")
        
        self.stdout.write(f"\n🗺️  Lugar asociado: {entrada_santiago.lugar_asociado.nombre}")
        self.stdout.write(f"📝 Entrada de blog: {entrada_santiago.titulo}")
        
        self.stdout.write("\n🚀 ¡Ya puedes probar tu blog desde el admin o el frontend!")
        self.stdout.write("   Admin: http://localhost:8000/admin/travel_api/fotografia/")
        self.stdout.write("   API: http://localhost:8000/api/entradas-blog/") 