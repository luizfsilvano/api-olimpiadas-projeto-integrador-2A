from django.contrib import admin
from django.urls import path
from OlimpiadasApp.views.views_user import *
from OlimpiadasApp.views.views_esportes import *
from OlimpiadasApp.views.views_atletas import *
from OlimpiadasApp.views.views_paises import *
from OlimpiadasApp.views.views_medalhas import *
from OlimpiadasApp.views.views_site import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    # Endpoint para teste
    path('hello', hello, name='hello'),

    # Pagina padrão de administração do Django
    path('admin', admin.site.urls),
    
    # Metodos de uso para Esportes
    path('esportes', create_esporte, name='esportes'),
    path('esportes/<str:_id>/partidas', create_match, name='partidas'),

    # Métodos de uso para Atletas
    path('atletas', get_atletas, name='atletas'),
    path('atletas/<str:pais_id>/<str:esporte_id>', create_atleta, name='atletas'),
    # Métodos de uso para Paises
    path('paises', create_pais, name='paises'),

    # Metodos de uso para Medalhas
    path('medalhas', medalhas_geral, name='medalhas'),
    path('medalhas/esportes', medalhas_por_esportes, name='medalhas_por_esportes'),
    path('medalhas/atletas', medalhas_por_atleta, name='medalhas_por_atleta'),
    path('medalhas/pais', medalhas_paises, name='medalhas_por_paises'),

    # Métodos de uso para autenticação
    path('login/token', login, name='login'),
    path('login/token/validar', protected_route, name='protected_route'),
    path('login/token/admin' , manage, name='manage'),

    # Método secreto para criar um superuser
    path('login/superuser', first_admin, name='create_superuser'),

    # Site principal para visualização
    path('', index, name='index'),
    path('boxe', boxe, name='boxe'),
    path('basquete', basquete, name='basquete'),
    path('futebol', futebol, name='futebol'),
    path('volei', volei, name='volei'),
    path('natacao', natacao, name='natacao'),
    path('100_metros_rasos', cem_metros_rasos, name='ginastica'),
    path('tiro_com_arco', tiro_com_arco, name='tiro_com_arco'),
    path('calendario', calendario, name='calendario'),
    path('quadro_de_medalhas', quadro_de_medalhas, name='quadro_de_medalhas'),
    path('registro', register, name='registro'),

]

if settings.DEBUG:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)