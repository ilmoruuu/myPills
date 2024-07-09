from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'app/index.html')

def login(request):
    return render(request, 'app/login.html')

def cadastro(request):
    return render(request, 'app/cadastro.html')

def remedios(request):
    return render(request, 'app/remedios.html')

def consultas(request):
    return render(request, 'app/consultas.html')

def perfil(request, user):
    user_num = {user}
    return render(request, 'app/perfil.html',
                  {'user': user_num})