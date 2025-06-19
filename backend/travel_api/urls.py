from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LugarViewSet, FotografiaViewSet, EntradaDeBlogViewSet, 
    mapa_data, entrada_blog_galeria, entrada_blog_por_slug, 
    entrada_blog_galeria_por_slug
)

router = DefaultRouter()
router.register(r'lugares', LugarViewSet)
router.register(r'fotografias', FotografiaViewSet)
router.register(r'entradas-blog', EntradaDeBlogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mapa-data/', mapa_data, name='mapa-data'),
    # URLs por ID (mantenidas para compatibilidad)
    path('entrada-blog-galeria/<int:entrada_id>/', entrada_blog_galeria, name='entrada-blog-galeria'),
    path('entrada-blog-galeria/<int:entrada_id>/<int:foto_id>/', entrada_blog_galeria, name='entrada-blog-galeria-foto'),
    # URLs por slug (nuevas)
    path('blog/<slug:slug>/', entrada_blog_por_slug, name='entrada-blog-slug'),
    path('blog/<slug:slug>/galeria/', entrada_blog_galeria_por_slug, name='entrada-blog-galeria-slug'),
    path('blog/<slug:slug>/galeria/<int:foto_id>/', entrada_blog_galeria_por_slug, name='entrada-blog-galeria-slug-foto'),
] 