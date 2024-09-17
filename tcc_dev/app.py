# Importação das bibliotecas e módulos
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
import mysql.connector

# import get_db_connection()
# from datetime import datetime
import resources.database_connection as database_connection

# Configuração do aplicativo da web
app = Flask(__name__)

# Chave de proteção contra CSRF (Cross-Site Request Forgery)
app.config['SECRET_KEY'] = 'manutenc@oTCC'

# Rota para o LOGIN
@app.route('/')
def login ():

    # Renderizar a página inicial
    return render_template('login.html')

# VALIDAR LOGIN
@app.route('/validar-login', methods=['POST'])
def validar_login():

    # Recupera as informações digitadas no formulário.
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Conecta ao banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Consulta o usuário pelo e-mail e senha
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
    usuario = cursor.fetchone()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    if usuario:

        # Verifica o nível de acesso
        nivel_acesso = usuario[5]
        
        if nivel_acesso == 1:
            return redirect(url_for('index1'))
        elif nivel_acesso == 2:
            return redirect(url_for('index2'))
        elif nivel_acesso == 3:
            return redirect(url_for('index3'))
        else:
            flash('Nível de acesso desconhecido', 'error')
            return redirect(url_for('login'))
    else:
        flash('As credenciais não conferem!!!', 'error')
        return redirect(url_for('login'))
    

# Rota para o CADASTRO
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro ():

     # Verifica se existe alguma requisição via POST
    if(request.method == 'POST'):

        # Recupera os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        nivel_acesso = request.form['nivel_acesso']
        numero_telefone = request.form['numero_telefone']
        cidade = request.form['cidade']

        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL e insere os dados no banco de dados
        SQL = "INSERT INTO usuarios (nome, cpf, email, senha, nivel_acesso, numero_telefone, cidade) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        values = (nome, cpf, email, senha, nivel_acesso, numero_telefone, cidade)
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Redireciona o usuário após cadastro dos dados no Banco de Dados
        return redirect(url_for('login'))

    else:
        return render_template('cadastro.html')

# Rota para o ESQUECI A SENHA
@app.route('/esqueci-senha',  methods=['GET', 'POST'])
def esqueci_senha ():

    # Verifica se existe alguma requisição via POST
    if(request.method == 'POST'):

        # Recupera as informações digitadas no formulário.
        email = request.form.get('email')

        # Conecta ao banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Consulta o usuário pelo e-mail e senha
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Se o usuario existir, redireciona para as telas com as perguntas
        if usuario:
            #Renderizar
            return render_template('recuperar_senha.html')
        
            # Recupera os dados do formulário
            cpf = request.form['cpf']
            numero_telefone = request.form['numero_telefone']
            cidade = request.form['cidade']

            # Faz a conexão com o banco de dados
            connection = database_connection.open_connection()
            cursor = connection.cursor()

            # Consulta o usuário pelo e-mail e senha
            cursor.execute("SELECT * FROM usuarios WHERE cpf = %s, numero_telefone = %s AND cidade = %s", (cpf, numero_telefone, cidade))
            perguntas = cursor.fetchone()

            # Fecha a conexão com o banco de dados
            cursor.close()
            connection.close()

            if perguntas:
                # Redireciona o usuário após cadastro dos dados no Banco de Dados
                return redirect(url_for('mudar_senha'))
            
            else:
                #Envia uma mensagem de erro
                flash('Dados incorretos...', 'error')
                return redirect(url_for('login'))
        
        else:

            #Envia uma mensagem de erro
            flash('Usuário não cadastrado...', 'error')
            return redirect(url_for('login'))
    
    else:

        #Renderizar
        return render_template('esqueci_senha.html')

# Rota para o MUDAR A SENHA
@app.route('/mudar_senha')
def mudar_senha ():

    #Renderizar
    return render_template('mudar_senha.html')

# Rota para o INDEX 1
@app.route('/index1')
def index1 ():

    #Renderizar
    return render_template('index1.html')

# Rota para o INDEX 2
@app.route('/index2')
def index2 ():

    #Renderizar
    return render_template('index2.html')

# Rota para o FAZER PEDIDO
@app.route('/fazer_pedido')
def fazer_pedido ():

    #Renderizar
    return render_template('fazer_pedido.html')

# Rota para o INDEX 3
@app.route('/index3')
def index3 ():

    #Renderizar
    return render_template('index3.html')



#!Não trazer para cima:
# Execução do aplicativo da web
if __name__ == '__main__':
    app.run(debug=True)