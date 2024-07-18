from django.shortcuts import render
from django.http import HttpResponse
from datetime import date, time
import psycopg2

def index(request):
    return render(request, 'app/index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        senha = request.POST["senha"]

        cursor = connect_bd().cursor()
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
    if request.method == 'POST':
        nome = request.POST["nome"]
        email = request.POST["email"]
        senha = request.POST["senha"]
        idade = request.POST["idade"]
        peso = request.POST["peso"]
        altura = request.POST["altura"]
        comorbidade = request.POST["comorbidade"]
        cpf = request.POST["CPF"]
        genero = request.POST["genero"]

        conn =  connect_bd()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO paciente (nome, email, senha, idade, peso, altura, comorbidade, cpf, genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (nome, email, senha, idade, peso, altura, comorbidade, cpf, genero)
            )
            conn.commit()
            return render(request, 'app/login.html')
        
        except Exception as erroCadastro:
            conn.rollback()
            return render(request, 'app/cadastro.html', {
                'mensagem': f'Erro ao cadastrar: {erroCadastro}'
            })  

        finally:
            cursor.close()
                 
    else:
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
    id_usuario = 1
    if request.method == 'POST':
        cursor = connect_bd().cursor()
        if 'add_remedio' in request.POST:
            remedio = request.POST['remedio']
            dosagem = request.POST['dosagem']
            lote = request.POST['lote']
            fabricacao = request.POST['fabricacao']
            validade = request.POST['validade']
            
            cursor.execute("""
            INSERT INTO remedio (nome_comercial, data_vencimento, data_fabricacao, dosagem, lote)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING idRemedio""",
                (remedio, validade, fabricacao, dosagem, lote))

            id_remedio = cursor.fetchone
            cursor.execute("""
                INSERT INTO historico (idPaciente)
                VALUES (%s)
                RETURNING idHistorico
            """, (id_usuario,))
            
            id_historico = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO registro_remedio (idPaciente, idRemedio, idHistorico, data, horario, quantidade)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_usuario, id_remedio, id_historico, date.today(), time(12, 0), 1.0))

            connect_bd().commit()
            connect_bd().close()

            return render(request, 'app/remedios.html', {
                "user": id_usuario
            })
            
        if 'add_consulta' in request.POST:
            medico = request.POST['medico']
            local = request.POST['local']
            dataHora = request.POST['dataHora']

            cursor.execute("""
            INSERT INTO consulta (nome_comercial, data_vencimento, data_fabricacao, dosagem, lote)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING idRemedio""",
                (remedio, validade, fabricacao, dosagem, lote))

            id_remedio = cursor.fetchone
            cursor.execute("""
                INSERT INTO historico (idPaciente)
                VALUES (%s)
                RETURNING idHistorico
            """, (id_usuario,))
            
            id_historico = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO registro_remedio (idPaciente, idRemedio, idHistorico, data, horario, quantidade)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_usuario, id_remedio, id_historico, date.today(), time(12, 0), 1.0))

            connect_bd().commit()
            connect_bd().close()

            return render(request, 'app/remedios.html', {
                "user": id_usuario
            })
        
    else:       
        return render(request, 'app/add.html')

def connect_bd():
    try:
        conn = psycopg2.connect(
            dbname="MyPills",
            user="postgres",
            password="marialaiz1",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as erroCadastro:
        print(f"Erro ao conectar ao banco de dados: {erroCadastro}")
        return None