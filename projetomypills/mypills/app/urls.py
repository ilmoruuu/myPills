from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('remedios/', views.remedios, name='remedios'),
    path('consultas/', views.consultas, name='consultas'),
    path('perfil/', views.perfil, name='perfil'),
    path('add/', views.add, name='add')
]