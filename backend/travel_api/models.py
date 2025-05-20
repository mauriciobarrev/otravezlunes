from django.db import models
from django.conf import settings # Para referenciar al User model
import uuid # Add this import

class Lugar(models.Model):
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    descripcion_corta = models.TextField(blank=True, null=True, help_text="Descripción breve para el pop-up del mapa.")
    foto_iconica_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL/path de la foto icónica para el pop-up.")
    # Podríamos añadir un campo para el tipo de marcador si fuera necesario diferenciarlo en la DB
    # tipo_marcador = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: solo_fotos, blog, favorito")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Lugares"
        unique_together = ['latitud', 'longitud'] # No deberían existir dos lugares exactamente en el mismo punto.

class Fotografia(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Identificador único universal para la fotografía.")
    lugar = models.ForeignKey(Lugar, related_name='fotografias', on_delete=models.CASCADE)
    url_imagen = models.URLField(max_length=500) # O models.ImageField si las vas a subir y servir directamente con Django
    thumbnail_url = models.URLField(max_length=550, blank=True, null=True, help_text="URL/path del thumbnail de la fotografía.")
    autor_fotografia = models.CharField(max_length=150, blank=True, null=True, help_text="Nombre de la persona que tomó la fotografía")
    fecha_toma = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    palabras_clave = models.CharField(max_length=255, blank=True, null=True, help_text="Separadas por comas.")
    es_foto_principal_lugar = models.BooleanField(default=False, help_text="Indica si esta es la foto icónica principal del Lugar (para el pop-up). Considerar lógica para asegurar solo una.")
    direccion_captura = models.TextField(blank=True, null=True, help_text="Dirección textual o descripción de la ubicación donde se tomó la foto.")

    def __str__(self):
        return f"Foto de {self.lugar.nombre} ({self.id})"
    
    class Meta:
        ordering = ['-fecha_toma']

class EntradaDeBlog(models.Model):
    titulo = models.CharField(max_length=255)
    lugar_asociado = models.ForeignKey(Lugar, related_name='entradas_blog', on_delete=models.SET_NULL, blank=True, null=True, help_text="Lugar principal al que se refiere esta entrada, si aplica.")
    # Se podrían asociar múltiples lugares a una entrada de blog con un ManyToManyField si fuera necesario.
    # lugares = models.ManyToManyField(Lugar, related_name='entradas_blog_asociadas', blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField(help_text="Soporta Markdown o texto enriquecido. El frontend deberá interpretarlo.")
    # Podríamos añadir un campo slug para URLs amigables
    # slug = models.SlugField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name_plural = "Entradas de Blog"
