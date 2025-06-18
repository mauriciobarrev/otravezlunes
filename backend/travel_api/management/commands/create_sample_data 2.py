from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel_api.models import Lugar, Fotografia
import os
import uuid
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para la aplicación'

    def handle(self, *args, **options):
        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superusuario creado'))
        
        # Crear algunos lugares de ejemplo
        lugares_datos = [
            {
                'nombre': 'Campo de Criptana',
                'ciudad': 'Campo de Criptana',
                'pais': 'España',
                'latitud': Decimal('39.4086'),
                'longitud': Decimal('-3.1244'),
                'descripcion_corta': 'Famoso por sus molinos de viento que inspiraron a Cervantes'
            },
            {
                'nombre': 'Consuegra',
                'ciudad': 'Consuegra',
                'pais': 'España',
                'latitud': Decimal('39.4625'),
                'longitud': Decimal('-3.6086'),
                'descripcion_corta': 'Hermoso pueblo con molinos históricos'
            },
            {
                'nombre': 'Pucón',
                'ciudad': 'Provincia de Cautín',
                'pais': 'Chile',
                'latitud': Decimal('-39.2719'),
                'longitud': Decimal('-71.9791'),
                'descripcion_corta': 'Hermosa ciudad lacustre al pie del volcán Villarrica'
            }
        ]
        
        for lugar_data in lugares_datos:
            lugar, created = Lugar.objects.get_or_create(
                nombre=lugar_data['nombre'],
                defaults=lugar_data
            )
            status = 'creado' if created else 'ya existente'
            self.stdout.write(self.style.SUCCESS(f'Lugar {lugar.nombre} {status}'))
        
        # Vincular fotos existentes a los lugares
        photos_dir = os.path.join(os.getcwd(), '..', 'photos')
        if not os.path.isdir(photos_dir):
            photos_dir = os.path.join(os.getcwd(), 'photos')
        
        if not os.path.isdir(photos_dir):
            self.stdout.write(self.style.WARNING(f'No se encuentra el directorio de fotos en: {photos_dir}'))
            return
        
        # Obtener lista de archivos en el directorio
        files = [f for f in os.listdir(photos_dir) if os.path.isfile(os.path.join(photos_dir, f)) 
                and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Asignar fotos a lugares
        lugar_criptana = Lugar.objects.filter(nombre='Campo de Criptana').first()
        lugar_consuegra = Lugar.objects.filter(nombre='Consuegra').first()
        lugar_pucon = Lugar.objects.filter(nombre='Pucón').first()
        
        fotos_asignacion = {
            lugar_criptana: ['IMG_1594.jpeg'],
            lugar_consuegra: ['IMG_1596.jpeg'],
            lugar_pucon: ['IMG_1621.jpeg']
        }
        
        for lugar, fotos_nombres in fotos_asignacion.items():
            if not lugar:
                continue
                
            for foto_nombre in fotos_nombres:
                if foto_nombre in files:
                    foto_path = os.path.join('photos', foto_nombre)
                    foto_uuid = str(uuid.uuid4())
                    
                    foto, created = Fotografia.objects.get_or_create(
                        url_imagen=foto_path,
                        defaults={
                            'lugar': lugar,
                            'uuid': foto_uuid,
                            'fecha_toma': datetime.now(),
                            'descripcion': f'Fotografía de {lugar.nombre}',
                            'es_foto_principal_lugar': True
                        }
                    )
                    
                    status = 'creada' if created else 'ya existente'
                    self.stdout.write(self.style.SUCCESS(f'Fotografía {foto_nombre} {status} para {lugar.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No se encontró la foto: {foto_nombre}'))
        
        # Imprimir estadísticas
        self.stdout.write(self.style.SUCCESS(f'Total de lugares en la base de datos: {Lugar.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total de fotografías en la base de datos: {Fotografia.objects.count()}')) 