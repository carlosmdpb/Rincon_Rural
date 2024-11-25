from django.contrib import admin
from django.urls import path
from .views import bienvenido, perfil_usuario, registro, LoginUsuario, cerrar_sesion, reservar_espacio
from calificaciones.views import valorar_app

urlpatterns = [
    path('', bienvenido, name='bienvenido'),  # Página de bienvenida
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('registro/', registro, name='registro'),
    path('login/', LoginUsuario.as_view(), name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('espacios/<int:espacio_id>/reservar/', reservar_espacio, name='reservar_espacio'),
    path('admin/', admin.site.urls),
    path('valorar_app/', valorar_app, name='valorar_app'),
]
