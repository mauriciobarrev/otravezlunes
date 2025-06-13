from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel_api.models import Lugar, EntradaDeBlog, Fotografia
from datetime import date, datetime
import random

class Command(BaseCommand):
    help = 'Crear datos de prueba para el blog de viajes con entradas y fotos agrupadas'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')
        
        # Crear usuario si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Mauro',
                'last_name': 'Administrador',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(f'Usuario creado: {user.username}')
        else:
            self.stdout.write(f'Usuario existente: {user.username}')

        # Crear lugares si no existen
        lugares_data = [
            {
                'nombre': 'Torres del Paine',
                'ciudad': 'Puerto Natales',
                'pais': 'Chile',
                'latitud': -50.9423,
                'longitud': -73.4068,
                'descripcion_corta': 'Parque Nacional con montañas espectaculares y lagos cristalinos'
            },
            {
                'nombre': 'Machu Picchu',
                'ciudad': 'Cusco',
                'pais': 'Perú',
                'latitud': -13.1631,
                'longitud': -72.5450,
                'descripcion_corta': 'Ciudadela inca en las montañas de los Andes peruanos'
            },
            {
                'nombre': 'Salar de Uyuni',
                'ciudad': 'Uyuni',
                'pais': 'Bolivia',
                'latitud': -20.1338,
                'longitud': -67.4891,
                'descripcion_corta': 'El desierto de sal más grande del mundo'
            },
            {
                'nombre': 'Valparaíso',
                'ciudad': 'Valparaíso',
                'pais': 'Chile',
                'latitud': -33.0472,
                'longitud': -71.6127,
                'descripcion_corta': 'Ciudad puerto llena de arte callejero y arquitectura colorida'
            }
        ]

        lugares = []
        for lugar_data in lugares_data:
            lugar, created = Lugar.objects.get_or_create(
                nombre=lugar_data['nombre'],
                defaults=lugar_data
            )
            lugares.append(lugar)
            if created:
                self.stdout.write(f'Lugar creado: {lugar.nombre}')
            else:
                self.stdout.write(f'Lugar existente: {lugar.nombre}')

        # URLs de fotos de ejemplo de Unsplash
        fotos_torres_paine = [
            'https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?q=80&w=3000',
            'https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=3000',
            'https://images.unsplash.com/photo-1548013146-72479768bada?q=80&w=3000',
            'https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=3000',
            'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=3000'
        ]

        fotos_machu_picchu = [
            'https://images.unsplash.com/photo-1587595431973-160d0d94add1?q=80&w=3000',
            'https://images.unsplash.com/photo-1526392060635-9d6019884377?q=80&w=3000',
            'https://images.unsplash.com/photo-1539650116574-75c0c6d13ec9?q=80&w=3000',
            'https://images.unsplash.com/photo-1582967788606-a171c1080cb0?q=80&w=3000'
        ]

        fotos_salar_uyuni = [
            'https://images.unsplash.com/photo-1544985361-b420d7a77043?q=80&w=3000',
            'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?q=80&w=3000',
            'https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=3000',
            'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=3000'
        ]

        fotos_valparaiso = [
            'https://images.unsplash.com/photo-1596466174679-10a2a8ac2b6c?q=80&w=3000',
            'https://images.unsplash.com/photo-1544943910-4c1dc44aab44?q=80&w=3000',
            'https://images.unsplash.com/photo-1531068956741-73b5e8bf0de5?q=80&w=3000'
        ]

        # Crear entradas de blog con fotos
        entradas_data = [
            {
                'titulo': 'Aventura en Torres del Paine: 5 días de trekking',
                'lugar': lugares[0],  # Torres del Paine
                'contenido': '''
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum. 
                Donec auctor blandit quam, et molestie ipsum tempus non. Nullam quis risus eget urna mollis ornare vel eu leo.
                
                Cras mattis consectetur purus sit amet fermentum. Sed posuere consectetur est at lobortis. 
                Nullam id dolor id nibh ultricies vehicula ut id elit. Maecenas sed diam eget risus varius blandit sit amet non magna.
                
                Vestibulum id ligula porta felis euismod semper. Cum sociis natoque penatibus et magnis dis parturient montes, 
                nascetur ridiculus mus. Donec sed odio dui. Vestibulum id ligula porta felis euismod semper.
                ''',
                'fotos': fotos_torres_paine
            },
            {
                'titulo': 'Machu Picchu al amanecer: Una experiencia inolvidable',
                'lugar': lugares[1],  # Machu Picchu
                'contenido': '''
                Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, 
                tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus.
                
                Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui. Lorem ipsum dolor sit amet, 
                consectetur adipiscing elit. Sed posuere consectetur est at lobortis.
                
                Cras justo odio, dapibus ac facilisis in, egestas eget quam. Vestibulum id ligula porta felis euismod semper.
                ''',
                'fotos': fotos_machu_picchu
            },
            {
                'titulo': 'Reflejos infinitos: 3 días en el Salar de Uyuni',
                'lugar': lugares[2],  # Salar de Uyuni
                'contenido': '''
                Cras mattis consectetur purus sit amet fermentum. Cras justo odio, dapibus ac facilisis in, egestas eget quam.
                Morbi leo risus, porta ac consectetur ac, vestibulum at eros.
                
                Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor.
                Aenean lacinia bibendum nulla sed consectetur. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.
                ''',
                'fotos': fotos_salar_uyuni
            },
            {
                'titulo': 'Arte urbano en Valparaíso: Recorrido por los cerros',
                'lugar': lugares[3],  # Valparaíso
                'contenido': '''
                Sed posuere consectetur est at lobortis. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.
                Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
                
                Maecenas faucibus mollis interdum. Donec id elit non mi porta gravida at eget metus.
                Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus.
                ''',
                'fotos': fotos_valparaiso
            }
        ]

        # Crear entradas de blog y sus fotografías
        for entrada_data in entradas_data:
            entrada, created = EntradaDeBlog.objects.get_or_create(
                titulo=entrada_data['titulo'],
                defaults={
                    'lugar_asociado': entrada_data['lugar'],
                    'autor': user,
                    'contenido': entrada_data['contenido']
                }
            )
            
            if created:
                self.stdout.write(f'Entrada de blog creada: {entrada.titulo}')
                
                # Crear fotografías para esta entrada
                for i, foto_url in enumerate(entrada_data['fotos']):
                    foto = Fotografia.objects.create(
                        lugar=entrada_data['lugar'],
                        entrada_blog=entrada,
                        url_imagen=foto_url,
                        thumbnail_url=foto_url + '&w=400&h=400&fit=crop',  # Thumbnail más pequeño
                        autor_fotografia='Mauro Barrev',
                        fecha_toma=date(2024, random.randint(1, 12), random.randint(1, 28)),
                        descripcion=f'Fotografía {i+1} de {entrada.titulo}',
                        orden_en_entrada=i,
                        es_foto_principal_lugar=(i == 0)  # La primera foto de la primera entrada será la principal
                    )
                    self.stdout.write(f'  Foto creada: {foto.descripcion}')
            else:
                self.stdout.write(f'Entrada de blog existente: {entrada.titulo}')

        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente!'))
        self.stdout.write('Ahora puedes ver el mapa con marcadores y galerías agrupadas por entrada de blog.') 