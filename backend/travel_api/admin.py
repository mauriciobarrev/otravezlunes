from django.contrib import admin
from .models import Lugar, Fotografia, EntradaDeBlog
from django.utils.html import format_html
from django.conf import settings

@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'pais', 'latitud', 'longitud')
    search_fields = ('nombre', 'ciudad', 'pais')
    list_filter = ('pais', 'ciudad')

    def get_queryset(self, request):
        # Mostrar todos los lugares (incluyendo los deshabilitados) en el admin
        return Lugar.all_objects.all()

@admin.register(Fotografia)
class FotografiaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'lugar', 'entrada_blog', 'thumbnail_preview', 'autor_fotografia', 'fecha_toma', 'orden_en_entrada')
    list_filter = ('lugar', 'entrada_blog', 'fecha_toma', 'es_foto_principal_lugar', 'autor_fotografia')
    search_fields = ('uuid', 'lugar__nombre', 'entrada_blog__titulo', 'descripcion', 'palabras_clave', 'autor_fotografia')
    readonly_fields = ('uuid', 'url_imagen', 'thumbnail_url', 'image_preview', 'thumbnail_preview_large')
    fields = ('lugar', 'entrada_blog', 'imagen', 'thumbnail', 'autor_fotografia', 'fecha_toma', 'descripcion', 'orden_en_entrada', 'es_foto_principal_lugar', 'uuid', 'url_imagen', 'thumbnail_url', 'image_preview', 'thumbnail_preview_large')

    def image_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="400" height="auto" />', obj.imagen.url)
        elif obj.url_imagen:
            # Construir URL completa para imágenes
            if obj.url_imagen.startswith('photos/'):
                image_full_url = f"/media/{obj.url_imagen}"
            else:
                image_full_url = obj.url_imagen
            return format_html('<img src="{}" width="400" height="auto" />', image_full_url)
        return "(No image)"
    image_preview.short_description = 'Vista Previa Imagen'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="70" height="auto" />', obj.thumbnail.url)
        elif obj.thumbnail_url:
            # Construir URL completa para thumbnails
            if obj.thumbnail_url.startswith('photos/'):
                thumbnail_full_url = f"/media/{obj.thumbnail_url}"
            else:
                thumbnail_full_url = obj.thumbnail_url
            return format_html('<img src="{}" width="70" height="auto" />', thumbnail_full_url)
        return "(No thumbnail)"
    thumbnail_preview.short_description = 'Miniatura'

    def thumbnail_preview_large(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="300" height="auto" />', obj.thumbnail.url)
        elif obj.thumbnail_url:
            # Construir URL completa para thumbnails
            if obj.thumbnail_url.startswith('photos/'):
                thumbnail_full_url = f"/media/{obj.thumbnail_url}"
            else:
                thumbnail_full_url = obj.thumbnail_url
            return format_html('<img src="{}" width="300" height="auto" />', thumbnail_full_url)
        return "(No thumbnail)"
    thumbnail_preview_large.short_description = 'Vista Previa Miniatura'

    def get_queryset(self, request):
        return Fotografia.all_objects.select_related('lugar', 'entrada_blog')

@admin.register(EntradaDeBlog)
class EntradaDeBlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'autor', 'fecha_display_formatted', 'fecha_publicacion', 'lugar_asociado', 'mostrar_solo_mes_anio')
    list_filter = ('autor', 'fecha_publicacion', 'lugar_asociado', 'mostrar_solo_mes_anio')
    search_fields = ('titulo', 'slug', 'contenido', 'autor__username', 'lugar_asociado__nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'slug', 'descripcion', 'lugar_asociado', 'autor')
        }),
        ('Configuración de Fecha', {
            'fields': ('fecha_evento', 'mostrar_solo_mes_anio'),
            'description': 'La fecha de evento es opcional. Si no se especifica, se usará la fecha de publicación. '
                          'Marcar "mostrar solo mes/año" para mostrar formato como "mayo 2024" en lugar de "14 de mayo de 2024".'
        }),
        ('Contenido', {
            'fields': ('contenido_markdown',),
            'classes': ('wide',)
        }),
        ('Metadatos del Sistema', {
            'fields': ('fecha_publicacion', 'contenido_html'),
            'classes': ('collapse',),
            'description': 'Campos automáticos del sistema. No editar manualmente.'
        })
    )
    
    readonly_fields = ('fecha_publicacion', 'contenido_html')
    
    def fecha_display_formatted(self, obj):
        """Muestra la fecha como se verá en el frontend"""
        fecha = obj.get_fecha_display()
        if obj.get_mostrar_solo_mes_anio():
            return fecha.strftime('%B %Y')  # "mayo 2024"
        else:
            return fecha.strftime('%d de %B de %Y')  # "14 de mayo de 2024"
    fecha_display_formatted.short_description = 'Fecha de Visualización'
    fecha_display_formatted.admin_order_field = 'fecha_evento'

    def get_queryset(self, request):
        return EntradaDeBlog.all_objects.select_related('autor', 'lugar_asociado')
