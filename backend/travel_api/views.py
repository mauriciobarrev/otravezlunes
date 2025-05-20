from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .models import Lugar, Fotografia, EntradaDeBlog
from .serializers import LugarSerializer, FotografiaSerializer, LugarDetalleSerializer
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
    GET /api/fotografias/{id}/ - Detalle de una fotografía específica
    """
    queryset = Fotografia.objects.all()
    serializer_class = FotografiaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filtra fotografías por lugar si se proporciona el parámetro"""
        queryset = super().get_queryset()
        lugar_id = self.request.query_params.get('lugar')
        if lugar_id:
            queryset = queryset.filter(lugar_id=lugar_id)
        return queryset
    
    def get_serializer_context(self):
        """Añade el request al contexto para obtener URLs absolutas"""
        context = super().get_serializer_context()
        return context

@api_view(['GET'])
@permission_classes([AllowAny])
def mapa_data(request):
    """
    Endpoint para obtener los datos necesarios para el mapa.
    Devuelve la lista de lugares con sus coordenadas, nombre y fotos icónicas.
    """
    lugares = Lugar.objects.all()
    resultado = []
    
    for lugar in lugares:
        # Obtener una fotografía representativa, si existe
        foto_principal = lugar.fotografias.filter(es_foto_principal_lugar=True).first()
        if not foto_principal:
            foto_principal = lugar.fotografias.first()
        
        thumbnail = None
        imagen_completa = None
        
        if foto_principal:
            # Construir URLs para miniaturas y imágenes completas
            if foto_principal.thumbnail_url:
                # La URL completa para el thumbnail
                thumbnail = request.build_absolute_uri('/media/' + foto_principal.thumbnail_url)
            
            if foto_principal.url_imagen:
                # La URL completa para la imagen
                imagen_completa = request.build_absolute_uri('/media/' + foto_principal.url_imagen)
        
        resultado.append({
            'id': lugar.id,
            'coordinates': [float(lugar.longitud), float(lugar.latitud)],
            'nombre': lugar.nombre,
            'ciudad': lugar.ciudad, 
            'pais': lugar.pais,
            'thumbnail': thumbnail,
            'imagen_completa': imagen_completa,
            'descripcion': lugar.descripcion_corta
        })
    
    return Response(resultado)
