from rest_framework import serializers
from .models import Lugar, Fotografia, EntradaDeBlog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class LugarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lugar
        fields = ['id', 'nombre', 'ciudad', 'pais', 'latitud', 'longitud', 'descripcion_corta', 'foto_iconica_url']

class FotografiaSerializer(serializers.ModelSerializer):
    # Campos del lugar
    lugar_nombre = serializers.CharField(source='lugar.nombre', read_only=True)
    lugar_ciudad = serializers.CharField(source='lugar.ciudad', read_only=True)
    lugar_pais = serializers.CharField(source='lugar.pais', read_only=True)
    coordenadas = serializers.SerializerMethodField()
    
    # Información de la entrada de blog
    entrada_blog_titulo = serializers.CharField(source='entrada_blog.titulo', read_only=True)
    entrada_blog_id = serializers.IntegerField(source='entrada_blog.id', read_only=True)
    
    # URLs absolutas para las imágenes
    imagen_url = serializers.SerializerMethodField()
    thumbnail_url_absoluta = serializers.SerializerMethodField()
    imagen_alta_calidad_url = serializers.SerializerMethodField()  # Nueva URL para imagen de alta calidad
    
    class Meta:
        model = Fotografia
        fields = [
            'id', 'uuid', 'lugar', 'lugar_nombre', 'lugar_ciudad', 'lugar_pais',
            'entrada_blog', 'entrada_blog_titulo', 'entrada_blog_id', 'orden_en_entrada',
            'imagen_url', 'thumbnail_url_absoluta', 'imagen_alta_calidad_url', 'autor_fotografia', 'fecha_toma',
            'descripcion', 'palabras_clave', 'coordenadas', 'direccion_captura'
        ]
    
    def get_coordenadas(self, obj):
        """Devuelve las coordenadas del lugar como un array [longitud, latitud]"""
        return [float(obj.lugar.longitud), float(obj.lugar.latitud)]
    
    def get_imagen_url(self, obj):
        """Devuelve la URL absoluta de la imagen"""
        request = self.context.get('request')
        if not request or not obj.url_imagen:
            return None
        
        # Extraer el nombre del archivo de la URL
        filename = obj.url_imagen.split('/')[-1]
        # Construir la URL apuntando directamente a la carpeta de fotos
        return request.build_absolute_uri(f'/media/photos/{filename}')
    
    def get_thumbnail_url_absoluta(self, obj):
        """Devuelve la URL absoluta del thumbnail"""
        request = self.context.get('request')
        if not request or not obj.thumbnail_url:
            return None
        
        # Extraer el nombre del archivo de thumbnail
        thumb_filename = obj.thumbnail_url.split('/')[-1]
        # Construir la URL apuntando directamente a la carpeta de thumbnails
        return request.build_absolute_uri(f'/media/photos/thumbnails/{thumb_filename}')
        
    def get_imagen_alta_calidad_url(self, obj):
        """Devuelve la URL absoluta de la imagen de alta calidad"""
        request = self.context.get('request')
        if not request:
            return None
        
        # Primero intentamos utilizar url_imagen si existe
        if obj.url_imagen:
            # Extraer el nombre del archivo de la URL para evitar problemas con rutas
            filename = obj.url_imagen.split('/')[-1]
            # Construir la URL directamente apuntando a la carpeta de fotos
            return request.build_absolute_uri(f'/media/photos/{filename}')
        
        # Si no hay url_imagen, intentamos inferir desde el thumbnail
        if obj.thumbnail_url and '_thumb.' in obj.thumbnail_url:
            # Extraer el nombre del archivo de thumbnail
            thumb_filename = obj.thumbnail_url.split('/')[-1]
            # Construir el nombre del archivo original
            original_filename = thumb_filename.replace('_thumb.', '.')
            # Devolver la URL completa
            return request.build_absolute_uri(f'/media/photos/{original_filename}')
        
        # Si no hay información suficiente, devolvemos None
        return None

class EntradaDeBlogConFotosSerializer(serializers.ModelSerializer):
    """Serializer para mostrar una entrada de blog con todas sus fotografías"""
    fotografias = FotografiaSerializer(many=True, read_only=True)
    autor_info = UserSerializer(source='autor', read_only=True)
    lugar_asociado_info = LugarSerializer(source='lugar_asociado', read_only=True)
    
    class Meta:
        model = EntradaDeBlog
        fields = [
            'id', 'titulo', 'lugar_asociado', 'lugar_asociado_info',
            'fecha_publicacion', 'autor', 'autor_info', 'contenido', 'fotografias'
        ]

class LugarDetalleSerializer(serializers.ModelSerializer):
    """Serializer para mostrar un lugar con todas sus entradas de blog y fotografías"""
    entradas_blog = EntradaDeBlogConFotosSerializer(many=True, read_only=True)
    fotografias = FotografiaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lugar
        fields = [
            'id', 'nombre', 'ciudad', 'pais', 'latitud', 'longitud',
            'descripcion_corta', 'foto_iconica_url', 'entradas_blog', 'fotografias'
        ]

class EntradaDeBlogSerializer(serializers.ModelSerializer):
    autor_info = UserSerializer(source='autor', read_only=True)
    lugar_asociado_info = LugarSerializer(source='lugar_asociado', read_only=True)

    class Meta:
        model = EntradaDeBlog
        fields = [
            'id',
            'titulo',
            'lugar_asociado', # FK
            'lugar_asociado_info',
            'fecha_publicacion',
            'autor', # FK
            'autor_info',
            'contenido'
        ]
        read_only_fields = ['autor_info', 'lugar_asociado_info'] 