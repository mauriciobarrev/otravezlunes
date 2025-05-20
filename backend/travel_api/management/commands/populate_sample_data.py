import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel_api.models import Lugar, Fotografia, EntradaDeBlog
from datetime import date

class Command(BaseCommand):
    help = 'Populates the database with sample travel data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Asegurarse de que existe un superusuario para asignar como autor
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123') # Cambia esto por una contraseña segura
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {admin_user.username} already exists.'))

        # Limpiar datos antiguos (opcional, cuidado en producción)
        Fotografia.objects.all().delete()
        EntradaDeBlog.objects.all().delete()
        Lugar.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared old data (Lugar, Fotografia, EntradaDeBlog).'))

        # Crear Lugares
        santiago, _ = Lugar.objects.get_or_create(
            nombre="Santiago", 
            pais="Chile", 
            ciudad="Santiago",
            latitud=Decimal("-33.45694"), # Centro aproximado
            longitud=Decimal("-70.64827")
        )
        valparaiso, _ = Lugar.objects.get_or_create(
            nombre="Valparaíso", 
            pais="Chile", 
            ciudad="Valparaíso",
            latitud=Decimal("-33.04583"),
            longitud=Decimal("-71.61972")
        )
        buenos_aires, _ = Lugar.objects.get_or_create(
            nombre="Buenos Aires", 
            pais="Argentina", 
            ciudad="Buenos Aires",
            latitud=Decimal("-34.603722"),
            longitud=Decimal("-58.381592")
        )
        self.stdout.write(self.style.SUCCESS('Created sample Lugares.'))

        # Crear Fotografias
        fotos_data = [
            # Santiago - Plaza de Armas (mismo punto, varias fotos)
            {'lugar': santiago, 'lat': "-33.437830", 'lon': "-70.650450", 'url': "https://source.unsplash.com/random/800x600?santiago,plaza,architecture", 'title': "Catedral Metropolitana", 'rep': True},
            {'lugar': santiago, 'lat': "-33.437830", 'lon': "-70.650450", 'url': "https://source.unsplash.com/random/800x600?santiago,plaza,people", 'title': "Ambiente en la Plaza", 'rep': False},
            {'lugar': santiago, 'lat': "-33.437830", 'lon': "-70.650450", 'url': "https://source.unsplash.com/random/800x600?santiago,plaza,statue", 'title': "Monumento en la Plaza", 'rep': False},
            # Santiago - Cerro San Cristobal (otro punto)
            {'lugar': santiago, 'lat': "-33.423706", 'lon': "-70.631813", 'url': "https://source.unsplash.com/random/800x600?santiago,hill,view", 'title': "Vista desde el Cerro", 'rep': True},
            {'lugar': santiago, 'lat': "-33.423900", 'lon': "-70.631900", 'url': "https://source.unsplash.com/random/800x600?santiago,teleferico", 'title': "Teleférico San Cristóbal", 'rep': False},
            # Santiago - Sky Costanera (otro punto)
            {'lugar': santiago, 'lat': "-33.417484", 'lon': "-70.606981", 'url': "https://source.unsplash.com/random/800x600?santiago,skycostanera,cityscape", 'title': "Santiago desde las alturas", 'rep': True},
            
            # Valparaíso - Cerro Alegre (varios puntos cercanos)
            {'lugar': valparaiso, 'lat': "-33.03870", 'lon': "-71.62830", 'url': "https://source.unsplash.com/random/800x600?valparaiso,mural,colorful", 'title': "Murales de Cerro Alegre", 'rep': True},
            {'lugar': valparaiso, 'lat': "-33.03910", 'lon': "-71.62790", 'url': "https://source.unsplash.com/random/800x600?valparaiso,street,art", 'title': "Callejón con encanto", 'rep': False},
            {'lugar': valparaiso, 'lat': "-33.04050", 'lon': "-71.62950", 'url': "https://source.unsplash.com/random/800x600?valparaiso,house,colored", 'title': "Casas coloridas", 'rep': True},
            # Valparaíso - Muelle Prat
            {'lugar': valparaiso, 'lat': "-33.040000", 'lon': "-71.620000", 'url': "https://source.unsplash.com/random/800x600?valparaiso,port,boats", 'title': "Barcos en el Muelle Prat", 'rep': True},

            # Buenos Aires - Obelisco (mismo punto)
            {'lugar': buenos_aires, 'lat': "-34.603737", 'lon': "-58.381576", 'url': "https://source.unsplash.com/random/800x600?buenosaires,obelisco,day", 'title': "Obelisco de día", 'rep': True},
            {'lugar': buenos_aires, 'lat': "-34.603737", 'lon': "-58.381576", 'url': "https://source.unsplash.com/random/800x600?buenosaires,obelisco,night", 'title': "Obelisco de noche", 'rep': False},
            # Buenos Aires - Caminito
            {'lugar': buenos_aires, 'lat': "-34.638056", 'lon': "-58.363056", 'url': "https://source.unsplash.com/random/800x600?buenosaires,caminito,tango", 'title': "Tango en Caminito", 'rep': True},
        ]

        for i, foto_info in enumerate(fotos_data):
            Fotografia.objects.create(
                lugar=foto_info['lugar'],
                latitud=Decimal(foto_info['lat']),
                longitud=Decimal(foto_info['lon']),
                url_imagen=foto_info['url'] + f"&sig={i}", # Añadir sig para evitar cache de Unsplash
                titulo_foto=foto_info['title'],
                descripcion=f"Descripción de ejemplo para {foto_info['title']}.",
                fecha_toma=date(2023, random.randint(1,12), random.randint(1,28)),
                es_foto_representativa_del_punto=foto_info['rep']
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(fotos_data)} sample Fotografias.'))

        # Crear Entradas de Blog de ejemplo
        EntradaDeBlog.objects.create(
            titulo="Mi Viaje a Santiago de Chile",
            lugar_asociado=santiago,
            autor=admin_user,
            contenido="# Santiago Increíble\nSantiago es una ciudad vibrante... (contenido en Markdown)"
        )
        EntradaDeBlog.objects.create(
            titulo="Colores y Colinas: Valparaíso",
            lugar_asociado=valparaiso,
            autor=admin_user,
            contenido="## Explorando Valparaíso\nUn puerto lleno de arte y escaleras... (contenido en Markdown)"
        )
        self.stdout.write(self.style.SUCCESS('Created sample EntradasDeBlog.'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!')) 