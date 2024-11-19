from django.urls import path
from .views import perfil_usuario, registro, LoginUsuario, cerrar_sesion, reservar_espacio

urlpatterns = [
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('registro/', registro, name='registro'),
    path('login/', LoginUsuario.as_view(), name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('espacios/<int:espacio_id>/reservar/', reservar_espacio, name='reservar_espacio'),
]
