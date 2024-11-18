# reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('', views.listar_reservas, name='listar_reservas'),
]
