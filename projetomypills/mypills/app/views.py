from django.shortcuts import redirect, render
from django.http import HttpResponse
from datetime import date, time, datetime
from twilio.rest import Client
import psycopg2

## AQUI TWILIO ##
account_sid = 'segredo'
auth_token = '[AuthToken]'
client = Client(account_sid, auth_token)

def index(request):
    user = request.session.get('user_id')
    return render(request, 'app/index.html', {
        'user': user
    })

def login(request):
    if request.method == 'POST':
        print(request.POST)
        email = request.POST["email"]
        senha = request.POST["senha"]

        cursor = connect_bd().cursor()
        cursor.execute("SELECT senha FROM paciente WHERE email = %s", (email,))
        resultado = cursor.fetchone()

        if (resultado):
            senhabd = resultado[0]
            if (senhabd == senha):
                cursor.execute("SELECT idPaciente FROM paciente WHERE email = %s", (email,))
                id_usuario = cursor.fetchone()
                request.session['user_id'] = id_usuario
                return redirect('perfil')
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
        print(request.POST)
        nome = request.POST["nome"]
        email = request.POST["email"]
        senha = request.POST["senha"]
        idade = request.POST["idade"]
        peso = request.POST["peso"]
        altura = request.POST["altura"]
        comorbidade = request.POST["comorbidade"]
        cpf = request.POST["cpf"]
        genero = request.POST["genero"]

        conexao =  connect_bd()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "INSERT INTO paciente (nome, email, senha, idade, peso, altura, comorbidade, cpf, genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (nome, email, senha, idade, peso, altura, comorbidade, cpf, genero)
            )
            conexao.commit()
        
        except Exception as erroCadastro:
            conexao.rollback()
            return render(request, 'app/cadastro.html', {
                'mensagem': f'Erro ao cadastrar: {erroCadastro}'
            })  

        finally:
            cursor.close()
            return redirect('login')
                 
    else:
        return render(request, 'app/cadastro.html')

def remedios(request):
    user_id = request.session.get('user_id')[0]
    user = get_user(user_id)
    remedios = get_remedios(user.id)
    if request.method == 'POST' and 'deletar' in request.POST:
        id_remedio = int(request.POST['id_remedio'])


        delete_remedio(id_remedio, user.id)
        return redirect('remedios')
    return render(request, 'app/remedios.html', {
        'user': user,
        'remedios': remedios
    })

def consultas(request):
    user_id = request.session.get('user_id')[0]
    user = get_user(user_id)
    consultas = get_consultas(user.id)

    if request.method == 'POST' and 'whatsapp' in request.POST and request.POST['value'] != "":
        print(request.POST['value'])

    if request.method == 'POST' and 'deletar' in request.POST:
        id_consulta = int(request.POST['id_consulta'])

        delete_consulta(id_consulta, user.id)
        return redirect('consultas')
    return render(request, 'app/consultas.html', {
        'user': user,
        'consultas': consultas
    })

def perfil(request):
    user_id = request.session.get('user_id')[0]
    user_info = get_user(user_id)
    if request.method == 'POST' and 'editar' in request.POST:
        nome = request.POST["nome"]
        email = request.POST["email"]
        senha = request.POST["senha"]
        idade = request.POST["idade"]
        peso = request.POST["peso"]
        altura = request.POST["altura"]
        comorbidade = request.POST["comorbidade"]
        cpf = request.POST["cpf"]
        genero = request.POST["genero"]

        try:
            conexao = connect_bd()
            cursor = conexao.cursor()
            cursor.execute("""UPDATE paciente SET nome = %s, email = %s, senha = %s, idade = %s, peso = %s, altura = %s, comorbidade = %s, cpf = %s, genero = %s WHERE idPaciente = %s""",
                (nome, email, senha, idade, peso, altura, comorbidade, cpf, genero, user))
        
        except Exception as erroCadastro:
            conexao.rollback()
            return render(request, 'app/perfil.html', {
                'mensagem': f'Erro ao atualizar: {erroCadastro}'
            })
        
        conexao.commit()
        conexao.close()

        user_info = get_user(user_id)

        return render(request, 'app/perfil.html', {
            'user': user_info
        })
    if request.method == 'POST' and 'logout' in request.POST:
        request.session.flush()
        return redirect('login')

    return render(request, 'app/perfil.html',
                  {'user': user_info})

def add(request):
    user_id = request.session.get('user_id')[0]
    user = get_user(user_id)
    if request.method == 'POST':
        conexao = connect_bd()
        cursor = conexao.cursor()
        if 'add_remedio' in request.POST:
            remedio = request.POST['remedio']
            dosagem = request.POST['dosagem']
            lote = request.POST['lote']
            fabricacao = request.POST['fabricacao']
            validade = request.POST['validade']
            horario = request.POST['horario']
            fabricacao = datetime.strptime(fabricacao, '%Y-%m-%d').date()
            validade = datetime.strptime(validade, '%Y-%m-%d').date()
            horario = datetime.strptime(horario, '%H:%M').time()
            try:
                cursor.execute("""
                INSERT INTO remedio (nome_comercial, data_vencimento, data_fabricacao, dosagem, lote, idPaciente, horario)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING idRemedio""",
                    (remedio, validade, fabricacao, dosagem, lote, user.id, horario))
                id_remedio = cursor.fetchone()[0]
            except Exception as erroCadastro:
                conexao.rollback()
                return render(request, 'app/add.html', {
                    'mensagem': f'Erro ao cadastrar: {erroCadastro}'
                })
            finally:
                print(f"{id_remedio} cadastrado!")
                conexao.commit()
                conexao.close()

            return redirect('remedios')
            
        if 'add_consulta' in request.POST:
            print(request.POST)
            medico = request.POST['medico']
            local = request.POST['local']
            datahr = request.POST['datahr']
            data, horario = datahr.split("T")

            data = datetime.strptime(data, '%Y-%m-%d').date()

            cursor.execute("""INSERT INTO historico (idPaciente)
                            VALUES (%s)
                            RETURNING idHistorico
                        """, (user.id,))
            id_historico = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO consulta (idPaciente, idHistorico, medico, local, data, horario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user.id, id_historico, medico, local, data, horario))

            conexao.commit()
            conexao.close()

            return redirect('consultas')
        
    else:       
        return render(request, 'app/add.html', {
            "user": user
        })

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
    
class User:
    def __init__(self, id, nome, email, senha, idade, peso, altura, comorbidade, cpf, genero):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.idade = idade
        self.peso = peso
        self.altura = altura
        self.comorbidade = comorbidade
        self.cpf = cpf
        self.genero = genero

class Remedio:
    def __init__(self, id, nome_comercial, data_vencimento, data_fabricacao, dosagem, lote, idPaciente, horario):
        self.id = id
        self.nome_comercial = nome_comercial
        self.data_vencimento = data_vencimento
        self.data_fabricacao = data_fabricacao
        self.dosagem = dosagem
        self.lote = lote
        self.idPaciente = idPaciente
        self.horario = horario

class Consulta:
    def __init__(self, id, idPaciente, idHistorico, horario, local, medico, data):
        self.id = id
        self.idPaciente = idPaciente
        self.idHistorico = idHistorico
        self.medico = medico
        self.local = local
        self.data = data
        self.horario = horario

def get_user(id):
    cursor = connect_bd().cursor()
    cursor.execute("SELECT * FROM paciente WHERE idPaciente = %s", (id,))
    result = cursor.fetchone()
    return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9])

def get_remedios(id):
    cursor = connect_bd().cursor()
    cursor.execute("SELECT * FROM remedio WHERE idPaciente = %s", (id,))
    result = cursor.fetchall()
    remedios = []
    for remedio in result:
        remedio_instance = Remedio(remedio[0], remedio[1], remedio[2], remedio[3], remedio[4], remedio[5], remedio[6], remedio[7])
        remedios.append(remedio_instance)
    return remedios

def get_consultas(id):
    cursor = connect_bd().cursor()
    cursor.execute("SELECT * FROM consulta WHERE idPaciente = %s", (id,))
    result = cursor.fetchall()
    consultas = []
    for consulta in result:
        consulta_instance = Consulta(consulta[0], consulta[1], consulta[2], consulta[3], consulta[4], consulta[5], consulta[6])
        consultas.append(consulta_instance)
    return consultas

def delete_remedio(remedio_id, user_id):
        conexao = connect_bd()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM remedio WHERE idRemedio = %s AND idPaciente = %s", (remedio_id, user_id))
        conexao.commit()
        cursor.close()
        conexao.close()
        return redirect('remedios')
        

def delete_consulta(consulta_id, user_id):
    conexao = connect_bd()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM consulta WHERE idConsulta = %s AND idPaciente = %s", (consulta_id, user_id))
    conexao.commit()
    cursor.close()
    conexao.close()
    return redirect('consultas')

print(get_remedios(1)[0].horario)