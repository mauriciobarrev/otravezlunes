import markdown
import bleach
from markdown.extensions import codehilite, toc, tables, fenced_code, admonition
import re
import logging

# Logger para el módulo
logger = logging.getLogger(__name__)

# Configuración de extensiones de Markdown
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',      # Incluye tables, fenced_code, footnotes, attr_list, def_list, abbr
    'markdown.extensions.codehilite', # Resaltado de sintaxis
    'markdown.extensions.toc',        # Tabla de contenidos
    'markdown.extensions.admonition', # Cajas de nota/warning/tip
    'markdown.extensions.nl2br',      # Convierte saltos de línea a <br>
]

# Configuración de Markdown
MARKDOWN_CONFIG = {
    'codehilite': {
        'css_class': 'highlight',
        'use_pygments': False,  # No usar pygments para evitar dependencias adicionales
        'noclasses': True,      # Incluir estilos inline
    },
    'toc': {
        'permalink': True,
        'permalink_class': 'headerlink',
        'permalink_title': 'Enlace permanente a este título',
    },
}

# Tags HTML permitidos después del procesamiento de Markdown
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'div', 'span',
    'strong', 'b', 'em', 'i', 'u', 'mark', 'del', 's',
    'sup', 'sub',
    'a', 'img',
    'ul', 'ol', 'li',
    'blockquote', 'cite',
    'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'dl', 'dt', 'dd',
    'hr',
    'details', 'summary',
    'abbr', 'address', 'time',
]

# Atributos permitidos
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'title'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class'],
    'table': ['class'],
    'th': ['scope', 'class'],
    'td': ['class'],
    'abbr': ['title'],
    'time': ['datetime'],
    'input': ['type', 'checked', 'disabled'],  # Para listas de tareas
}

def markdown_to_html(markdown_text):
    """
    Convierte texto Markdown a HTML seguro.
    
    Args:
        markdown_text (str): Texto en formato Markdown
        
    Returns:
        str: HTML seguro y procesado
    """
    if not markdown_text:
        return ''
    
    # Configurar el procesador de Markdown
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_CONFIG,
    )
    
    # Convertir Markdown a HTML
    html = md.convert(markdown_text)
    
    # Limpiar HTML para seguridad (prevenir XSS)
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    # Post-procesamiento para mejorar la presentación
    clean_html = _post_process_html(clean_html)
    
    return clean_html

def _post_process_html(html):
    """
    Post-procesa el HTML para mejorar la presentación.
    """
    # Agregar clases CSS para styling
    html = re.sub(r'<blockquote>', '<blockquote class="blog-quote">', html)
    html = re.sub(r'<table>', '<table class="blog-table">', html)
    html = re.sub(r'<pre>', '<pre class="blog-code">', html)
    html = re.sub(r'<img', '<img class="blog-image"', html)
    
    # Hacer que los enlaces externos abran en nueva pestaña
    html = re.sub(
        r'<a href="(https?://[^"]*)"([^>]*)>',
        r'<a href="\1" target="_blank" rel="noopener noreferrer"\2>',
        html
    )
    
    return html

def extract_excerpt(markdown_text, max_length=200):
    """
    Extrae un extracto del contenido Markdown (sin HTML).
    
    Args:
        markdown_text (str): Texto en formato Markdown
        max_length (int): Longitud máxima del extracto
        
    Returns:
        str: Extracto de texto plano
    """
    if not markdown_text:
        return ''
    
    # Remover elementos de Markdown para obtener texto plano
    plain_text = re.sub(r'#{1,6}\s+', '', markdown_text)  # Headers
    plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', plain_text)  # Bold
    plain_text = re.sub(r'\*(.*?)\*', r'\1', plain_text)  # Italic
    plain_text = re.sub(r'!\[.*?\]\(.*?\)', '', plain_text)  # Images
    plain_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', plain_text)  # Links
    plain_text = re.sub(r'`([^`]+)`', r'\1', plain_text)  # Code
    plain_text = re.sub(r'\n+', ' ', plain_text)  # Multiple newlines
    plain_text = plain_text.strip()
    
    if len(plain_text) <= max_length:
        return plain_text
    
    # Truncar en la palabra más cercana
    truncated = plain_text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # Si el último espacio está cerca del final
        truncated = truncated[:last_space]
    
    return truncated + '...'

def validate_markdown(markdown_text):
    """
    Valida que el Markdown sea procesable y seguro.
    
    Args:
        markdown_text (str): Texto en formato Markdown
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not markdown_text:
        return True, None
    
    try:
        # Intentar procesar el Markdown
        html = markdown_to_html(markdown_text)
        
        # Verificaciones adicionales
        if len(markdown_text) > 100000:  # 100KB límite
            return False, "El contenido es demasiado largo"
        
        return True, None
        
    except Exception as e:
        return False, f"Error al procesar Markdown: {str(e)}"

def create_thumbnail(image, size=(300, 300)):
    """
    Crea un thumbnail de una imagen.
    
    Args:
        image: ImageField de Django
        size: Tupla con el tamaño del thumbnail (width, height)
        
    Returns:
        ImageField: Thumbnail generado
    """
    try:
        from PIL import Image
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        import os
        
        # Abrir la imagen original
        img = Image.open(image)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Crear thumbnail manteniendo las proporciones
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Generar nombre del archivo thumbnail
        name, ext = os.path.splitext(image.name)
        thumbnail_name = f"{name}_thumb{ext}"
        
        # Guardar thumbnail en memoria
        from io import BytesIO
        temp_thumb = BytesIO()
        img.save(temp_thumb, format='JPEG', quality=85)
        temp_thumb.seek(0)
        
        # Crear ContentFile para Django
        thumbnail_file = ContentFile(temp_thumb.read())
        thumbnail_file.name = thumbnail_name
        
        return thumbnail_file
        
    except Exception as e:
        # Usar logging para capturar el stacktrace sin exponer en consola en producción
        logger.exception("Error creando thumbnail: %s", e)
        return None 