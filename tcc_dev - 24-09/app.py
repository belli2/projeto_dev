# Importação das bibliotecas e módulos
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
import mysql.connector
# import get_db_connection()
# from datetime import datetime
import resources.database_connection as database_connection
import hashlib

# Configuração do aplicativo da web
app = Flask(__name__)

# Chave de proteção contra CSRF (Cross-Site Request Forgery)
app.config['SECRET_KEY'] = 'manutenc@oTCC'

# Rota para o LOGIN
@app.route('/')
def login ():

    # Renderizar a página inicial
    return render_template('login.html')

# Rota para o VALIDAR LOGIN
@app.route('/validar-login', methods=['POST'])
def validar_login():

    # Recupera as informações digitadas no formulário.
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Criptografa a senha do usuário
    senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()

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

        # Armazena o ID do usuário na sessão
        session['idUsuarios'] = usuario[0]  # Supondo que o ID do usuário seja o primeiro elemento

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

        # Criptografa a senha do usuário
        senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()

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
        flash('Cadastro realizado com sucesso!!!', 'sucess')
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
    
    else:

        #Renderizar
        return render_template('esqueci_senha.html')
    
# Rota para o RECUPERER SENHA
@app.route('/recuperar-senha',  methods=['GET', 'POST'])
def recuperar_senha ():

    if request.method == 'POST':
        email = request.form['email']
        cpf = request.form['cpf']
        numero_telefone = request.form['numero_telefone']
        cidade = request.form['cidade']

        connection = database_connection.open_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND cpf = %s AND numero_telefone = %s AND cidade = %s", (email, cpf, numero_telefone, cidade))
        perguntas = cursor.fetchone()

        cursor.close()
        connection.close()

        if perguntas:
            return redirect(url_for('mudar_senha', user_id=perguntas[0]))  # Supondo que perguntas[0] seja o ID do usuário
        else:
            flash('Dados incorretos...', 'error')
            return redirect(url_for('login'))

        # if perguntas:
        #     return redirect(url_for('mudar_senha'))
        # else:
        #     flash('Dados incorretos...', 'error')
        #     return redirect(url_for('login'))

    return render_template('recuperar_senha.html')

# Rota para o MUDAR A SENHA

@app.route('/mudar_senha/<int:user_id>', methods=['GET', 'POST'])
def mudar_senha(user_id):
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']

        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Atualiza a senha do usuário específico no banco de dados
        cursor.execute("UPDATE usuarios SET senha = %s WHERE idUsuarios = %s", (nova_senha, user_id))
        connection.commit()  # Certifique-se de confirmar a transação

        # Verifica se alguma linha foi afetada
        if cursor.rowcount > 0:
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao mudar a senha. Verifique se o usuário está correto.', 'error')

        cursor.close()
        connection.close()
        
    # Renderizar o formulário de mudança de senha
    return render_template('mudar_senha.html', user_id=user_id)

# @app.route('/mudar_senha', methods=['GET', 'POST'])
# def mudar_senha():
#     if request.method == 'POST':
#         # email = request.form['email']
#         nova_senha = request.form['nova_senha']

#         connection = database_connection.open_connection()
#         cursor = connection.cursor()

#         # Atualiza a senha do usuário no banco de dados
#         cursor.execute("UPDATE usuarios SET senha = %s", (nova_senha, ))
#         connection.commit()  # Certifique-se de confirmar a transação

#         # Verifica se alguma linha foi afetada
#         if cursor.rowcount > 0:
#             flash('Senha alterada com sucesso!', 'success')
#             return redirect(url_for('login'))
#         else:
#             flash('Erro ao mudar a senha. Verifique se o email está correto.', 'error')

#         cursor.close()
#         connection.close()
        
#     # Renderizar o formulário de mudança de senha
#     return render_template('mudar_senha.html')

# Rota para o INDEX 1
@app.route('/index1')
def index1 ():

     # Faz a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Monta a instrução SQL de seleção
    SQL = "SELECT data, descricao, local FROM ordem_manutencao WHERE ativo = 1;"

    # Executa a consulta SQL
    cursor.execute(SQL)

    # Cria um vetor com os resultados da consulta 
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    #Renderizar
    return render_template('index1.html', ordens=ordens)

# Rota para o EDITAR PEDIDO
@app.route('/editar-pedido', methods=['GET', 'POST'])
def editar_pedido(idOrdemManutencao=None):

    if request.method == 'POST':
        idOrdemManutencao = request.form['idOrdemManutencao']
        data = request.form['data']
        descricao = request.form['descricao']
        local = request.form['local']
        imagem = request.files['imagem']
        prioridade = request.form['prioridade']

        # Converte o arquivo de imagem para o formato binário (BLOB).
        blob = imagem.read() 

        # Conecta ao banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Insere o idUsuarios na instrução SQL
        SQL = "INSERT INTO ordem_manutencao (idOrdemManutencao, data, descricao, local, imagem, prioridade) VALUES (%s, %s, %s, %s, %s, %s);"
        values = (idOrdemManutencao, data, descricao, local, blob, prioridade)
        cursor.execute(SQL, values)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Editado com sucesso!', 'sucess')
        return render_template('index1.html')

    else:
        return render_template('editar_pedido.html')

# Rota para o INDEX 2
@app.route('/index2')
def index2 ():

    #Renderizar
    return render_template('index2.html')

# Rota para o FAZER PEDIDO
@app.route('/fazer_pedido', methods=['GET', 'POST'])
def fazer_pedido():

    if request.method == 'POST':
        data = request.form['data']
        descricao = request.form['descricao']
        local = request.form['local']
        imagem = request.files['imagem']

        # Converte o arquivo de imagem para o formato binário (BLOB).
        blob = imagem.read() 

        # Obtém o ID do usuário da sessão
        idUsuarios = session.get('idUsuarios')  # Obtém o ID do usuário logado

        if not idUsuarios:

            flash('Você precisa esta logado para fazer um pedido.', 'error')
            return redirect(url_for('login'))

        # Conecta ao banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Insere o idUsuarios na instrução SQL
        SQL = "INSERT INTO ordem_manutencao (data, descricao, local, imagem, idUsuarios) VALUES (%s, %s, %s, %s, %s);"
        values = (data, descricao, local, blob, idUsuarios)
        cursor.execute(SQL, values)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Pedido realizado com sucesso!!!', 'sucess')
        return render_template('index2.html')

    else:
        return render_template('fazer_pedido.html')

# Rota para o INDEX 3
@app.route('/index3')
def index3 (): #função de visualização

    # try:
    #     connection = database_connection.open_connection()
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT data, descricao, local FROM ordem_manutencao;")
    #     ordens = cursor.fetchall()
    # except Exception as e:
    #     flash('Erro ao conectar ao banco de dados.', 'error')
    #     ordens = []
    # finally:
    #     cursor.close()
    #     connection.close()

    # return render_template('index3.html', ordens=ordens)

    # Faz a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Monta a instrução SQL de seleção
    SQL = "SELECT data, descricao, local FROM ordem_manutencao;"
    # SQL = "SELECT data, descricao, local FROM ordem_manutencao WHERE ativo = 1;"

    # Executa a consulta SQL
    cursor.execute(SQL)

    # Cria um vetor com os resultados da consulta 
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    #Renderizar
    return render_template('index3.html', ordens=ordens)

if __name__ == '__main__':
    app.run(debug=True)

#!Não trazer para cima:

# Execução do aplicativo da web
if __name__ == '__main__':
    app.run(debug=True)