from django.shortcuts import render
from django.http import HttpResponse
import psycopg2

def index(request):
    return render(request, 'app/index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        senha = request.POST["senha"]

        cursor = connect_db().cursor()
        cursor.execute("SELECT senha FROM paciente WHERE email = %s", (email,))
        resultado = cursor.fetchone()
        if (resultado):
            senhabd = resultado[0]

            if (senhabd == senha):
                return render(request, 'app/index.html')
            else:
                return render(request, 'app/login.html', {
                    'mensagem': 'Senha incorreta'
                })
        else:
            return render(request, 'app/login.html', {
                    'mensagem': 'Email não cadastrado'
                })
    else:
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

def add(request):
    return render(request, 'app/add.html')

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="MyPills",
            user="postgres",
            password="ilmoru0407",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None