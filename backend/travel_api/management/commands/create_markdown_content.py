from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel_api.models import Lugar, EntradaDeBlog, Fotografia

class Command(BaseCommand):
    help = 'Crea contenido de ejemplo con formato Markdown'

    def handle(self, *args, **options):
        # Obtener o crear un usuario de ejemplo
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Administrador',
                'is_superuser': True,
                'is_staff': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario creado: {user.username}'))

        # Buscar lugares existentes o crear uno de ejemplo
        lugares = Lugar.objects.all()
        if not lugares.exists():
            lugar = Lugar.objects.create(
                nombre="Santiago de Chile",
                pais="Chile",
                ciudad="Santiago",
                latitud=-33.4489,
                longitud=-70.6693,
                descripcion_corta="La vibrante capital de Chile, rodeada de montañas majestuosas."
            )
            self.stdout.write(self.style.SUCCESS(f'Lugar creado: {lugar.nombre}'))
        else:
            lugar = lugares.first()

        # Crear entrada de blog con contenido Markdown rico
        markdown_content = """
# Mi Aventura en Santiago de Chile

Santiago me recibió con los brazos abiertos y un **cielo despejado** que prometía días llenos de *aventuras increíbles*. La capital chilena es una ciudad que combina perfectamente la modernidad urbana con la majestuosidad natural de Los Andes.

## Primeras Impresiones

Al llegar al aeropuerto, lo primero que me impactó fue la vista de las montañas nevadas que rodean la ciudad. El contraste entre los rascacielos del centro financiero y los picos andinos es simplemente **espectacular**.

### El Barrio Bellavista

Mi primera parada fue el colorido barrio de Bellavista, conocido por:

- **Arte callejero** de clase mundial
- Restaurantes con la mejor comida chilena
- Vida nocturna vibrante
- La casa de *Pablo Neruda* (La Chascona)

> "Santiago no es solo una ciudad, es una experiencia que te marca el alma" - reflexión personal después de mi primer día.

## Gastronomía Imperdible

La comida chilena fue una revelación constante. Algunos platos que **no puedes perderte**:

1. **Empanadas de pino** - Las mejores las encontré en el Mercado Central
2. **Cazuela** - Perfecta para los días fríos
3. **Completo italiano** - El hot dog más patriótico del mundo
4. **Mote con huesillo** - El refresco tradicional perfecto para el calor

### Tabla de Restaurantes Recomendados

| Restaurante | Especialidad | Precio | Ubicación |
|-------------|--------------|--------|-----------|
| Boragó | Cocina de autor | $$$ | Las Condes |
| El Hoyo | Comida criolla | $ | Centro |
| Azul Profundo | Mariscos | $$ | Providencia |

## Aventuras en Los Andes

### Cerro San Cristóbal

El ascenso al **Cerro San Cristóbal** es obligatorio. Puedes subir de varias formas:

- 🚡 En funicular (la opción clásica)
- 🚶‍♂️ Caminando por los senderos
- 🚗 En auto hasta la cumbre

La vista panorámica de 360° de Santiago es algo que quedará grabado en mi memoria para siempre.

### Valle de Maipo

A solo una hora de Santiago, el Valle de Maipo ofrece:

```
Experiencias imperdibles:
- Cata de vinos en viñas famosas
- Cabalgatas por los viñedos
- Gastronomía maridada con vinos locales
- Vistas espectaculares de Los Andes
```

## Reflexiones Finales

Santiago de Chile me enseñó que **viajar no es solo ver lugares nuevos**, sino *abrir la mente* a nuevas culturas, sabores y experiencias. La calidez de su gente, la riqueza de su cultura y la belleza de sus paisajes hacen de esta ciudad un destino que recomiendo con el corazón.

---

*¿Has visitado Santiago? ¡Me encantaría conocer tu experiencia en los comentarios!*

### Datos Útiles del Viaje

- **Duración**: 5 días
- **Época**: Marzo (otoño)
- **Clima**: Templado, días soleados
- **Presupuesto**: Medio
- **Recomendación**: ⭐⭐⭐⭐⭐ (5/5 estrellas)

~~Inicialmente pensé que 3 días serían suficientes~~ pero definitivamente necesitas al menos una semana para conocer bien la ciudad y sus alrededores.

> 💡 **Tip de viajero**: Descarga la app del Metro de Santiago, te ahorrará mucho tiempo y dinero en transporte.
"""

        # Crear o actualizar la entrada de blog
        entrada, created = EntradaDeBlog.objects.get_or_create(
            titulo="Mi Aventura en Santiago de Chile",
            defaults={
                'lugar_asociado': lugar,
                'autor': user,
                'contenido_markdown': markdown_content,
                'descripcion': 'Una experiencia inolvidable explorando la vibrante capital chilena, desde sus barrios bohemios hasta las majestuosas montañas que la rodean.'
            }
        )

        if not created:
            entrada.contenido_markdown = markdown_content
            entrada.save()

        action = 'creada' if created else 'actualizada'
        self.stdout.write(
            self.style.SUCCESS(f'Entrada de blog {action}: {entrada.titulo}')
        )

        # Verificar que el HTML se generó correctamente
        if entrada.contenido_html:
            self.stdout.write(
                self.style.SUCCESS('✓ Contenido HTML generado automáticamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠ No se pudo generar el contenido HTML')
            )

        self.stdout.write(
            self.style.SUCCESS('\n¡Contenido de ejemplo creado exitosamente!')
        )
        self.stdout.write(
            'Para verlo en acción:'
        )
        self.stdout.write(
            '1. Ejecuta el servidor: python manage.py runserver'
        )
        self.stdout.write(
            '2. Visita: http://localhost:8000/api/entradas-blog/'
        )
        self.stdout.write(
            f'3. O directo: http://localhost:8000/api/entradas-blog/{entrada.id}/'
        ) 