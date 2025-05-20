from django.contrib import admin
from .models import Lugar, Fotografia, EntradaDeBlog
from django.utils.html import format_html
from django.conf import settings

@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad', 'pais', 'latitud', 'longitud')
    search_fields = ('nombre', 'ciudad', 'pais')
    list_filter = ('pais', 'ciudad')

@admin.register(Fotografia)
class FotografiaAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'lugar', 'thumbnail_preview', 'autor_fotografia', 'fecha_toma', 'es_foto_principal_lugar', 'direccion_captura')
    list_filter = ('lugar', 'fecha_toma', 'es_foto_principal_lugar', 'autor_fotografia')
    search_fields = ('uuid', 'lugar__nombre', 'descripcion', 'palabras_clave', 'autor_fotografia', 'direccion_captura')
    readonly_fields = ('uuid', 'image_preview', 'thumbnail_preview_large')

    def image_preview(self, obj):
        if obj.url_imagen:
            # Añadimos el prefijo MEDIA_URL a la ruta de la imagen
            image_url = f"{settings.MEDIA_URL}{obj.url_imagen}"
            return format_html('<img src="{}" width="400" height="auto" />', image_url)
        return "(No image)"
    image_preview.short_description = 'Image Preview'

    def thumbnail_preview(self, obj):
        if obj.thumbnail_url:
            # Añadimos el prefijo MEDIA_URL a la ruta del thumbnail
            thumb_url = f"{settings.MEDIA_URL}{obj.thumbnail_url}"
            return format_html('<img src="{}" width="70" height="auto" />', thumb_url)
        return "(No thumbnail)"
    thumbnail_preview.short_description = 'Thumbnail'

    def thumbnail_preview_large(self, obj):
        if obj.thumbnail_url:
            # Añadimos el prefijo MEDIA_URL a la ruta del thumbnail
            thumb_url = f"{settings.MEDIA_URL}{obj.thumbnail_url}"
            return format_html('<img src="{}" width="300" height="auto" />', thumb_url)
        return "(No thumbnail)"
    thumbnail_preview_large.short_description = 'Thumbnail Preview (Large)'

@admin.register(EntradaDeBlog)
class EntradaDeBlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha_publicacion', 'lugar_asociado')
    list_filter = ('autor', 'fecha_publicacion', 'lugar_asociado')
    search_fields = ('titulo', 'contenido', 'autor__username', 'lugar_asociado__nombre')
    # Para el campo 'contenido' que podría ser Markdown, se podría integrar un editor de Markdown como `django-markdownx`.
