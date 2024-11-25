from django.urls import path
from usuarios.views import perfil_usuario

urlpatterns = [
    path('perfil/', perfil_usuario, name='perfil_usuario'),
]
