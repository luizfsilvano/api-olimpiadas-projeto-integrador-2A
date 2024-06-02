from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .views_esportes import *
from django.shortcuts import redirect
from django import forms
from Olimpiadas.settings import SECRET_KEY, db_user
import requests
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def boxe(request):
    return render(request, 'boxe.html')

def basquete(request):
    return render(request, 'basquete.html')

def futebol(request):
    return render(request, 'futebol.html')

def volei(request):
    return render(request, 'volei.html')

def natacao(request):
    return render(request, 'natacao.html')

def cem_metros_rasos(request):
    return render(request, '100_metros_rasos.html')

def tiro_com_arco(request):
    return render(request, 'tiro_com_arco.html')

def calendario(request):    
    errors = {}
    url = 'https://olimpiadasiesb-7780607c931d.herokuapp.com/esportes/partidas'
    # Pegar o token do servidor
    token_response = requests.post('https://olimpiadasiesb-7780607c931d.herokuapp.com/login/token', data={
        'username': db_user,
        'password': SECRET_KEY
    })
    if token_response.status_code != 200:
        errors['token'] = ["Erro ao obter token de autenticação."]
    else:
        token = token_response.json().get('token')
        if not token:
            errors['token'] = ["Erro ao obter token de autenticação."]

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    eventos = response.json()
    print(eventos)
    return render(request, 'calendario.html', {'eventos': eventos})

def quadro_de_medalhas(request):
    errors = {}
    url = 'https://olimpiadasiesb-7780607c931d.herokuapp.com/medalhas'
    # Pegar o token do servidor
    token_response = requests.post('https://olimpiadasiesb-7780607c931d.herokuapp.com/login/token', data={
        'username': db_user,
        'password': SECRET_KEY
    })
    if token_response.status_code != 200:
        errors['token'] = ["Erro ao obter token de autenticação."]
    else:
        token = token_response.json().get('token')
        if not token:
            errors['token'] = ["Erro ao obter token de autenticação."]

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    
    # Verificar o conteúdo da resposta
    try:
        dados = response.json()
    except ValueError:
        return HttpResponse("Erro ao processar a resposta da API: não é um JSON válido.", status=500)

    if not isinstance(dados, list):
        return HttpResponse("Erro: A resposta da API não é uma lista de países e medalhas.", status=500)

    # Processar os dados para calcular o total de medalhas e ordenar
    for pais in dados:
        try:
            pais['total'] = pais['ouro'] + pais['prata'] + pais['bronze']
            pais['pais'] = pais['pais'].title()
        except KeyError:
            return HttpResponse("Erro: Formato inesperado dos dados recebidos da API.", status=500)
    
    dados_ordenados = sorted(dados, key=lambda x: (-x['total'], -x['ouro'], -x['prata'], -x['bronze']))

    context = {
        'medalhas': dados_ordenados
    }

    return render(request, 'quadro_de_medalhas.html', context)

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match')


def register(request):
    errors = {}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Pegar o token do servidor
                token_response = requests.post('https://olimpiadasiesb-7780607c931d.herokuapp.com/login/token', data={
                    'username': db_user,
                    'password': SECRET_KEY
                })
                if token_response.status_code != 200:
                    errors['token'] = ["Erro ao obter token de autenticação."]
                else:
                    token = token_response.json().get('token')
                    if not token:
                        errors['token'] = ["Erro ao obter token de autenticação."]
                    else:
                        # Criar um novo usuário
                        response = requests.post('https://olimpiadasiesb-7780607c931d.herokuapp.com/login/token/admin', data={
                            'username': form.cleaned_data.get('username'),
                            'password': form.cleaned_data.get('password1'),
                            'user_type': 'juiz'
                        }, headers={
                            'Authorization': f'Bearer {token}'
                        })
                        print(response.json())
                        print(response.status_code)
                        if response.status_code == 201:
                            
                            return redirect('index')
                        else:
                            if response.status_code == 409:
                                errors['form'] = ["Usuário já existe."]
                            else:
                                server_errors = response.json()
                                for key, value in server_errors.items():
                                    errors[key] = value
            except requests.exceptions.RequestException as e:
                errors['request'] = [f"Erro na solicitação ao servidor: {str(e)}"]
        else:
            errors['form'] = form.errors.get_json_data()
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registro.html', {'form': form, 'errors':errors})