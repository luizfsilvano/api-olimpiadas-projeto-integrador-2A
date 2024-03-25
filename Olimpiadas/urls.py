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
    path('atletas', get_atletas, name='atletas'),
    path('atletas/<str:pais_id>/<str:esporte_id>', create_atleta, name='atletas'),
    path('atletas/<str:atleta_id>', get_and_delete_atleta , name='atletas'),

    # Métodos de uso para Paises
    path('paises', create_pais, name='paises'),

    # Métodos de uso para autenticação
    path('login/token', login, name='login'),
    path('login/token/validar', protected_route, name='protected_route'),
    path('login/token/admin' , manage, name='manage'),

    # Método secreto para criar um superuser
    path('login/superuser', first_admin, name='create_superuser')

]
