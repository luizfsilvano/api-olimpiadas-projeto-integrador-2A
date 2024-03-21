from django.contrib import admin
from django.urls import path
from OlimpiadasApp.views.views_user import *
from OlimpiadasApp.views.views_olimpiadas import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('esportes/', create_esporte, name='create_esporte'),
    path('juiz/token', login, name='login'),
    path('juiz/token/validar', protected_route, name='protected_route'),
    path('juiz/token/admin' , manage, name='register'),
]
