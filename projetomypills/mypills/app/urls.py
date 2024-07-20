from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('remedios/<int:user>', views.remedios, name='remedios'),
    path('consultas/<int:user>', views.consultas, name='consultas'),
    path('perfil/<int:user>', views.perfil, name='perfil'),
    path('add/<int:user>', views.add, name='add')
]