from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .models import Lugar, Fotografia, EntradaDeBlog
from .serializers import (
    LugarSerializer, FotografiaSerializer, LugarDetalleSerializer,
    EntradaDeBlogSerializer, EntradaDeBlogConFotosSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

class LugarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista para listar y recuperar lugares.
    GET /api/lugares/ - Lista todos los lugares
    GET /api/lugares/{id}/ - Detalle de un lugar específico
    """
    queryset = Lugar.objects.all()
    serializer_class = LugarSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LugarDetalleSerializer
        return LugarSerializer

class FotografiaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista para listar y recuperar fotografías.
    GET /api/fotografias/ - Lista todas las fotografías
    GET /api/fotografias/?lugar={id} - Lista fotografías de un lugar específico
    GET /api/fotografias/?entrada_blog={id} - Lista fotografías de una entrada de blog específica
    GET /api/fotografias/{id}/ - Detalle de una fotografía específica
    """
    queryset = Fotografia.objects.all()
    serializer_class = FotografiaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filtra fotografías por lugar o entrada de blog si se proporciona el parámetro"""
        queryset = super().get_queryset()
        lugar_id = self.request.query_params.get('lugar')
        entrada_blog_id = self.request.query_params.get('entrada_blog')
        
        if lugar_id:
            queryset = queryset.filter(lugar_id=lugar_id)
        elif entrada_blog_id:
            queryset = queryset.filter(entrada_blog_id=entrada_blog_id)
            
        return queryset
    
    def get_serializer_context(self):
        """Añade el request al contexto para obtener URLs absolutas"""
        context = super().get_serializer_context()
        return context

class EntradaDeBlogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista para listar y recuperar entradas de blog.
    GET /api/entradas-blog/ - Lista todas las entradas de blog
    GET /api/entradas-blog/{id}/ - Detalle de una entrada de blog específica con sus fotos
    GET /api/entradas-blog/?lugar={id} - Lista entradas de blog de un lugar específico
    """
    queryset = EntradaDeBlog.objects.all()
    serializer_class = EntradaDeBlogSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EntradaDeBlogConFotosSerializer
        return EntradaDeBlogSerializer
    
    def get_queryset(self):
        """Filtra entradas de blog por lugar si se proporciona el parámetro"""
        queryset = super().get_queryset()
        lugar_id = self.request.query_params.get('lugar')
        if lugar_id:
            queryset = queryset.filter(lugar_asociado_id=lugar_id)
        return queryset

@api_view(['GET'])
@permission_classes([AllowAny])
def mapa_data(request):
    """
    Endpoint para obtener los datos necesarios para el mapa.
    Devuelve marcadores individuales para cada foto, agrupados por entradas de blog.
    """
    lugares = Lugar.objects.all()
    resultado = []
    
    for lugar in lugares:
        # Obtener todas las entradas de blog de este lugar
        entradas_blog = lugar.entradas_blog.all()
        
        if entradas_blog.exists():
            # Para cada entrada de blog, crear marcadores para cada foto
            for entrada in entradas_blog:
                fotos_entrada = entrada.fotografias.all().order_by('orden_en_entrada')
                
                for foto in fotos_entrada:
                    # Crear un marcador individual para cada foto
                    marcador = {
                        'id': f"{lugar.id}-{entrada.id}-{foto.id}",  # ID único combinado
                        'lugar_id': lugar.id,
                        'entrada_id': entrada.id,
                        'foto_id': foto.id,
                        'coordinates': [float(lugar.longitud), float(lugar.latitud)],
                        'nombre': lugar.nombre,
                        'ciudad': lugar.ciudad,
                        'pais': lugar.pais,
                        'thumbnail': foto.thumbnail_url,
                        'imagen_completa': foto.url_imagen,
                        'descripcion': lugar.descripcion_corta,
                        'entrada_titulo': entrada.titulo,
                        'foto_orden': foto.orden_en_entrada,
                        'foto_descripcion': foto.descripcion,
                        'tipo_marcador': 'foto_blog'  # Identificador del tipo
                    }
                    resultado.append(marcador)
        else:
            # Para lugares sin entradas de blog, mantener comportamiento original
            foto_principal = lugar.fotografias.filter(es_foto_principal_lugar=True).first()
            if not foto_principal:
                foto_principal = lugar.fotografias.first()
            
            thumbnail = None
            imagen_completa = None
            
            if foto_principal:
                thumbnail = foto_principal.thumbnail_url
                imagen_completa = foto_principal.url_imagen
            
            marcador = {
                'id': lugar.id,
                'lugar_id': lugar.id,
                'coordinates': [float(lugar.longitud), float(lugar.latitud)],
                'nombre': lugar.nombre,
                'ciudad': lugar.ciudad,
                'pais': lugar.pais,
                'thumbnail': thumbnail,
                'imagen_completa': imagen_completa,
                'descripcion': lugar.descripcion_corta,
                'tipo_marcador': 'lugar_simple'  # Identificador del tipo
            }
            resultado.append(marcador)
    
    return Response(resultado)

@api_view(['GET'])
@permission_classes([AllowAny])
def entrada_blog_galeria(request, entrada_id, foto_id=None):
    """
    Endpoint para obtener datos completos de una entrada de blog con su galería.
    Si se especifica foto_id, devuelve el índice de esa foto para abrir la galería en esa posición.
    """
    try:
        entrada = EntradaDeBlog.objects.get(id=entrada_id)
        lugar = entrada.lugar_asociado
        
        # Obtener todas las fotos de esta entrada, ordenadas
        fotos_entrada = entrada.fotografias.all().order_by('orden_en_entrada')
        
        # Determinar el índice de la foto activa
        foto_activa_index = 0
        if foto_id:
            try:
                foto_activa = fotos_entrada.get(id=foto_id)
                foto_activa_index = list(fotos_entrada).index(foto_activa)
            except Fotografia.DoesNotExist:
                pass  # Usar índice 0 por defecto
        
        # Preparar datos de las fotos
        fotos_data = []
        for foto in fotos_entrada:
            foto_data = {
                'id': foto.id,
                'uuid': str(foto.uuid),
                'url': foto.url_imagen,
                'thumbnail': foto.thumbnail_url,
                'caption': foto.descripcion,
                'description': foto.descripcion,
                'date': foto.fecha_toma.strftime('%Y-%m-%d') if foto.fecha_toma else None,
                'orden': foto.orden_en_entrada
            }
            fotos_data.append(foto_data)
        
        # Preparar respuesta
        response_data = {
            'lugar': {
                'id': lugar.id,
                'nombre': lugar.nombre,
                'ciudad': lugar.ciudad,
                'pais': lugar.pais,
                'descripcion': lugar.descripcion_corta
            },
            'entrada': {
                'id': entrada.id,
                'titulo': entrada.titulo,
                'descripcion': entrada.descripcion,
                'contenido': entrada.contenido,
                'fecha_publicacion': entrada.fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S')
            },
            'fotos': fotos_data,
            'foto_activa_index': foto_activa_index
        }
        
        return Response(response_data)
        
    except EntradaDeBlog.DoesNotExist:
        return Response({'error': 'Entrada de blog no encontrada'}, status=404)
