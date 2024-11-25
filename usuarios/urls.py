from django.contrib import admin
from django.urls import path
from .views import bienvenido, crear_espacio, crear_evento, gestionar_reserva, perfil_administrador, perfil_usuario, registro, LoginUsuario, cerrar_sesion, reservar_espacio

urlpatterns = [
    path('', bienvenido, name='bienvenido'),  # Página de bienvenida
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('registro/', registro, name='registro'),
    path('login/', LoginUsuario.as_view(), name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('espacios/<int:espacio_id>/reservar/', reservar_espacio, name='reservar_espacio'),
    path('perfil_administrador/', perfil_administrador, name='perfil_administrador'),
    path('crear_evento/', crear_evento, name='crear_evento'),
    path('crear_espacio/', crear_espacio, name='crear_espacio'),
    path('gestionar_reserva/<int:reserva_id>/', gestionar_reserva, name='gestionar_reserva'),
    path('admin/', admin.site.urls)
]
