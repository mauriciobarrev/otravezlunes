from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LugarViewSet, FotografiaViewSet, mapa_data

router = DefaultRouter()
router.register(r'lugares', LugarViewSet)
router.register(r'fotografias', FotografiaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mapa-data/', mapa_data, name='mapa-data'),
] 