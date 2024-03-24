from django.contrib import admin
from django.urls import path
from OlimpiadasApp.views.views_user import *
from OlimpiadasApp.views.views_esportes import *
from OlimpiadasApp.views.views_atletas import *
from OlimpiadasApp.views.views_paises import *

urlpatterns = [
    # Pagina padrão de administração do Django
    path('admin', admin.site.urls),
    
    # Metodos de uso para Esportes
    path('esportes', create_esporte, name='esportes'),
    path('esportes/<str:_id>/partidas', create_match, name='partidas'),

    # Métodos de uso para Atletas
    path('atletas', create_atleta, name='atletas'),

    # Métodos de uso para Paises
    path('paises', create_pais, name='paises'),

    # Métodos de uso para autenticação
    path('login/token', login, name='login'),
    path('login/token/validar', protected_route, name='protected_route'),
    path('login/token/admin' , manage, name='manage'),

]
