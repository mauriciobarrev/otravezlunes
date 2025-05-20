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
        fields = '__all__'

class FotografiaSerializer(serializers.ModelSerializer):
    lugar_info = LugarSerializer(source='lugar', read_only=True) # Para anidar info del lugar

    class Meta:
        model = Fotografia
        fields = [
            'id',
            'lugar', # FK al ID de Lugar (para POST/PUT)
            'lugar_info', # Objeto Lugar anidado (para GET)
            'latitud',
            'longitud',
            'url_imagen',
            'fecha_toma',
            'descripcion',
            'titulo_foto',
            'palabras_clave',
            'es_foto_representativa_del_punto'
        ]
        # Si quieres que 'lugar' sea escribible por ID pero 'lugar_info' sea solo lectura.
        read_only_fields = ['lugar_info']


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