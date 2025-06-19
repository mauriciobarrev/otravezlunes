from django.db import models
from django.conf import settings # Para referenciar al User model
import uuid # Add this import
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Gestión de estados activo / deshabilitado
# -----------------------------------------------------------------------------


class StatusChoices(models.TextChoices):
    ACTIVE = 'active', _('Active')
    DISABLED = 'disabled', _('Disabled')


class StatusQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=StatusChoices.ACTIVE)


class StatusManager(models.Manager):
    def get_queryset(self):
        # Por defecto solo elementos activos
        return StatusQuerySet(self.model, using=self._db).filter(status=StatusChoices.ACTIVE)

    def all_with_disabled(self):
        return StatusQuerySet(self.model, using=self._db)


class StatusModel(models.Model):
    """Modelo abstracto que añade un campo 'status'."""

    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    # Managers
    objects = StatusManager()      # Solo activos
    all_objects = models.Manager() # Todos

    class Meta:
        abstract = True

class Lugar(StatusModel):
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    # Aumentamos la precisión para aceptar coordenadas copiadas directamente de
    # Google Maps (≈ 15 decimales).
    # max_digits debe ser >= dígitos enteros + decimal_places.
    # Latitud oscila entre -90 y 90  → máx 2 enteros; longitud entre -180 y 180 → 3.
    # 18 permite 3 enteros + 15 decimales.
    latitud = models.DecimalField(max_digits=18, decimal_places=15)
    longitud = models.DecimalField(max_digits=18, decimal_places=15)
    descripcion_corta = models.TextField(blank=True, null=True, help_text="Descripción breve para el pop-up del mapa.")
    foto_iconica_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL/path de la foto icónica para el pop-up.")
    # Podríamos añadir un campo para el tipo de marcador si fuera necesario diferenciarlo en la DB
    # tipo_marcador = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: solo_fotos, blog, favorito")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Lugares"
        unique_together = ['latitud', 'longitud'] # No deberían existir dos lugares exactamente en el mismo punto.

class Fotografia(StatusModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Identificador único universal para la fotografía.")
    lugar = models.ForeignKey(Lugar, related_name='fotografias', on_delete=models.CASCADE)
    entrada_blog = models.ForeignKey('EntradaDeBlog', related_name='fotografias', on_delete=models.CASCADE, null=True, blank=True, help_text="Entrada de blog a la que pertenece esta fotografía.")
    imagen = models.ImageField(upload_to='photos/', blank=True, null=True, help_text="Imagen principal de la fotografía")
    thumbnail = models.ImageField(upload_to='photos/thumbnails/', blank=True, null=True, help_text="Thumbnail de la fotografía (se genera automáticamente si no se especifica)")
    # Campos de compatibilidad para URLs (se llenan automáticamente)
    url_imagen = models.CharField(max_length=500, blank=True, help_text="URL generada automáticamente")
    thumbnail_url = models.CharField(max_length=550, blank=True, null=True, help_text="URL del thumbnail generada automáticamente")
    autor_fotografia = models.CharField(max_length=150, blank=True, null=True, help_text="Nombre de la persona que tomó la fotografía")
    fecha_toma = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    palabras_clave = models.CharField(max_length=255, blank=True, null=True, help_text="Separadas por comas.")
    es_foto_principal_lugar = models.BooleanField(default=False, help_text="Indica si esta es la foto icónica principal del Lugar (para el pop-up). Considerar lógica para asegurar solo una.")
    direccion_captura = models.TextField(blank=True, null=True, help_text="Dirección textual o descripción de la ubicación donde se tomó la foto.")
    orden_en_entrada = models.PositiveIntegerField(default=0, help_text="Orden de la fotografía dentro de la entrada de blog.")

    def __str__(self):
        return f"Foto de {self.lugar.nombre} ({self.id})"
    
    class Meta:
        ordering = ['entrada_blog', 'orden_en_entrada', '-fecha_toma']

class EntradaDeBlog(StatusModel):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción breve de la entrada de blog para mostrar en el hero.")
    lugar_asociado = models.ForeignKey(Lugar, related_name='entradas_blog', on_delete=models.SET_NULL, blank=True, null=True, help_text="Lugar principal al que se refiere esta entrada, si aplica.")
    # Se podrían asociar múltiples lugares a una entrada de blog con un ManyToManyField si fuera necesario.
    # lugares = models.ManyToManyField(Lugar, related_name='entradas_blog_asociadas', blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    
    # Campos flexibles para fechas de visualización
    fecha_evento = models.DateField(blank=True, null=True, help_text="Fecha del evento/viaje. Si no se especifica día, usar el primer día del mes.")
    mostrar_solo_mes_anio = models.BooleanField(default=False, help_text="Si está marcado, solo se mostrará 'mes año' (ej: 'mayo 2024'). Si no, se mostrará la fecha completa.")
    
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido_markdown = models.TextField(blank=True, null=True, help_text="Contenido en formato Markdown. Soporta títulos, negritas, cursivas, enlaces, listas, código, etc.")
    contenido_html = models.TextField(blank=True, null=True, help_text="Contenido convertido automáticamente a HTML desde Markdown. No editar manualmente.")
    # Campo temporal para migración - mantener compatibilidad
    contenido = models.TextField(blank=True, null=True, help_text="Campo temporal para migración. Usar contenido_markdown.")
    # Campo slug para URLs amigables
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="URL amigable generada automáticamente desde el título. Ej: catedral-colonia")
    
    # Mantener compatibilidad temporal con el campo anterior
    def get_contenido_procesado(self):
        """Retorna el contenido HTML procesado, priorizando contenido_html"""
        return self.contenido_html or self.contenido_markdown or self.contenido or ""
    
    def get_fecha_display(self):
        """Retorna la fecha a mostrar según la configuración"""
        if self.fecha_evento:
            return self.fecha_evento
        return self.fecha_publicacion.date()
    
    def get_mostrar_solo_mes_anio(self):
        """Retorna True si se debe mostrar solo mes y año"""
        return self.mostrar_solo_mes_anio
    
    def generate_slug(self):
        """Genera un slug único desde el título"""
        if not self.titulo:
            return ""
        
        base_slug = slugify(self.titulo)
        slug = base_slug
        counter = 1
        
        # Asegurar que el slug sea único
        while EntradaDeBlog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name_plural = "Entradas de Blog"

# Signal para auto-convertir Markdown a HTML y generar slug
@receiver(pre_save, sender=EntradaDeBlog)
def convert_markdown_to_html(sender, instance, **kwargs):
    """
    Signal que convierte automáticamente el contenido Markdown a HTML
    y genera el slug antes de guardar la entrada de blog.
    """
    from .utils import markdown_to_html
    
    if instance.contenido_markdown:
        instance.contenido_html = markdown_to_html(instance.contenido_markdown)
    
    # Generar slug automáticamente si no existe
    if not instance.slug and instance.titulo:
        instance.slug = instance.generate_slug()

# Signal para auto-generar URLs y thumbnails de fotografías
from django.db.models.signals import post_save

@receiver(post_save, sender=Fotografia)
def generate_image_urls_and_thumbnail(sender, instance, created, **kwargs):
    """
    Signal que genera automáticamente las URLs de las imágenes
    y crea thumbnails después de guardar.
    """
    if instance.imagen and not instance.thumbnail:
        try:
            # Crear thumbnail
            from .utils import create_thumbnail
            thumbnail_file = create_thumbnail(instance.imagen)
            
            if thumbnail_file:
                # Guardar el thumbnail sin activar signals infinitos
                instance.thumbnail.save(
                    thumbnail_file.name,
                    thumbnail_file,
                    save=False
                )
                
                # Actualizar URLs sin activar signals
                Fotografia.objects.filter(pk=instance.pk).update(
                    url_imagen=instance.imagen.url,
                    thumbnail_url=instance.thumbnail.url
                )
        except Exception as e:
            # Registrar el error usando logging para evitar prints en producción
            logger.exception("Error generando thumbnail: %s", e)
    
    # Actualizar URLs si no están establecidas
    if instance.imagen and not instance.url_imagen:
        Fotografia.objects.filter(pk=instance.pk).update(
            url_imagen=instance.imagen.url
        )
