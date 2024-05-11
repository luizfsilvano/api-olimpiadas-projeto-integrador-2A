from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .views_esportes import *
from django.shortcuts import redirect
from django import forms
import requests


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
    return render(request, 'calendario.html')

def quadro_de_medalhas(request):
    return render(request, 'quadro_de_medalhas.html')

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
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Pegar o token do servidor
            token_response = requests.post('http://127.0.0.1:8000/login/token', data = {
                'username': "luizfsilvano",
                'password': "Lfss@160505"
            })
            print(token_response.json())
            token = token_response.json()['token']
            # Criar um novo usuário
            response = requests.post('http://127.0.0.1:8000/login/token/admin', data = {
                'username': form.cleaned_data.get('username'),
                'password': form.cleaned_data.get('password1'),
                'user_type': 'juiz'
            }, headers = {
                'Authorization': f'Bearer {token}'
            })

            if response.status_code == 201:
                return redirect('index')
            else:
                print (response.json())
                pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})
