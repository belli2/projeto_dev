# Importação das bibliotecas e módulos
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
import base64

# import get_db_connection()
# from datetime import datetime
import resources.database_connection as database_connection
import hashlib

# from flask import Flask, send_file, abort
# import sqlite3  # ou psycopg2 para PostgreSQL
# import io  # Para manipular os dados da imagem como um stream


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
    
# Rota para o RECUPERAR SENHA
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

        # Criptografa a nova senha do usuário
        nova_senha = hashlib.sha256(nova_senha.encode('utf-8')).hexdigest()

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

# Rota para o LOGOUT
@app.route('/logout')
def logout():
    # Remove dados da sessão do usuário
    session.pop('user_id', None)
    # Redireciona o usuário para a página de login
    return redirect(url_for('login'))

# Rota para o INDEX 1
@app.route('/index1')
def index1 ():

    # Faz a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Monta a instrução SQL de seleção
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade FROM ordem_manutencao WHERE ativo = 1;"

    # Executa a consulta SQL
    cursor.execute(SQL)

    # Cria um vetor com os resultados da consulta 
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    todas_ordens = []

    # Calcula a situação de cada empréstimo
    for ordem in ordens:

        # Recupera as informações de data
        prioridade = ordem[4]

        # Verifica se o empréstimo está em dia ou atrasado
        if (prioridade == 0): categoria = "Não definida"
        if (prioridade == 1): categoria = "Alta"
        if (prioridade == 2): categoria = "Média"
        if (prioridade == 3): categoria = "Baixa"

        # Converte cada linha do banco de dados para lista
        ordem_atual = list(ordem)
        ordem_atual.append(categoria)

        # Adiciona o empréstimo atualizado na lista com todos os empréstimos
        todas_ordens.append(ordem_atual)  

    #Renderizar
    return render_template('index1.html', ordens=todas_ordens)

# Rota para o EDITAR PEDIDO
# @app.route('/editar-pedido', methods=['POST'])
# @app.route('/editar-pedido/<idOrdemManutencao>', methods=['GET'])
# def editar_pedido(idOrdemManutencao=None):
#     # Verifica se o método da requisição é o POST
#     if request.method == 'POST':
#         # Recebe os dados do formulário via POST
#         data = request.form['data']
#         descricao = request.form['descricao']
#         local = request.form['local']
#         imagem = request.form['imagem']
#         prioridade = request.form['prioridade']

#         # Faz conexão com o banco de dados
#         connection = database_connection.open_connection()
#         cursor = connection.cursor()

#         # Monta a instrução SQL para atualizar os dados
#         SQL = "UPDATE ordem_manutencao SET data = %s, descricao = %s, local = %s, imagem = %s, prioridade = %s WHERE idOrdemManutencao = %s;"
#         values = (data, descricao, local, imagem, prioridade, idOrdemManutencao)

#         try:
#             cursor.execute(SQL, values)
#             connection.commit()
#         except Exception as e:
#             connection.rollback()
#             print("Erro ao atualizar o pedido:", e)
#         finally:
#             cursor.close()
#             connection.close()

#         # Redireciona para a página de listagem de pedidos
#         return redirect(url_for('listar_pedido'))

#     else:
#         # Verifica se o idOrdemManutencao foi passado
#         if idOrdemManutencao is None:
#             return "ID do pedido não fornecido", 400

#         # Faz a conexão com o banco de dados
#         connection = database_connection.open_connection()
#         cursor = connection.cursor()

#         # Monta a instrução SQL para selecionar o pedido específico
#         SQL = "SELECT data, descricao, local, imagem, prioridade FROM ordem_manutencao WHERE idOrdemManutencao = %s;"
#         cursor.execute(SQL, (idOrdemManutencao,))
#         ordem = cursor.fetchone()

#         # Verifica se a ordem foi encontrada
#         if ordem is None:
#             return "Pedido não encontrado", 404

#         # Fecha a conexão com o banco de dados
#         cursor.close()
#         connection.close()

#         # Retorna a página HTML de edição do pedido com os dados preenchidos
#         return render_template('editar_pedido.html', ordem=ordem)


# Rota para o EDITAR PEDIDO
@app.route('/editar-pedido', methods=['POST'])
@app.route('/editar-pedido/<idOrdemManutencao>', methods=['GET'])
def editar_pedido(idOrdemManutencao=None):

    # Verifica se o método da requisição é o POST
    if(request.method == 'POST'):

        # Recebe os dados do formulário via POST
        idOrdemManutencao = request.form['idOrdemManutencao']
        prioridade = request.form['prioridade']

        # Faz conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL para atualizar os dados do leitor
        SQL = "UPDATE ordem_manutencao SET prioridade = %s WHERE idOrdemManutencao = %s;"
        values = (prioridade, idOrdemManutencao)
        print(SQL)
        print(f'Esse é o ID {idOrdemManutencao}, essa é a prioridade {prioridade}')
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Redireciona para a página de listagem de leitores
        return redirect(url_for('index1'))
    else:
        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL para selecionar o leitor com base no CPF
        SQL = "SELECT idOrdemManutencao, data, descricao, local, imagem, prioridade FROM ordem_manutencao WHERE idOrdemManutencao = %s;"
        
        # SQL = "SELECT data, descricao, local, imagem, prioridade FROM ordem_manutencao;"
        cursor.execute(SQL, (idOrdemManutencao,))
        ordem = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Verifica se a imagem existe e converte para um formato que o HTML pode usar
        imagem_base64 = None
        if ordem[4]:
            imagem_base64 = base64.b64encode(ordem[4]).decode('utf-8')
            imagem_base64 = f"data:image/jpeg;base64,{imagem_base64}"

        # Retorna a página HTML de edição do leitor com os dados preenchidos
        return render_template('editar_pedido.html', ordem=ordem, imagem=imagem_base64)

# @app.route('/editar-pedido')
# def editar_pedido ():

    #Renderizar
    # return render_template('editar_pedido.html')

# Rota para o EDITAR PEDIDO
# @app.route('/editar-pedido', methods=['GET', 'POST'])
# def editar_pedido(idOrdemManutencao=None):

    # if request.method == 'POST':
    #     idOrdemManutencao = request.form['idOrdemManutencao']
    #     data = request.form['data']
    #     descricao = request.form['descricao']
    #     local = request.form['local']
    #     imagem = request.files['imagem']
    #     prioridade = request.form['prioridade']

    #     # Converte o arquivo de imagem para o formato binário (BLOB).
    #     blob = imagem.read() 

    #     # Conecta ao banco de dados
    #     connection = database_connection.open_connection()
    #     cursor = connection.cursor()

    #     # Insere o idUsuarios na instrução SQL
    #     SQL = "INSERT INTO ordem_manutencao (idOrdemManutencao, data, descricao, local, imagem, prioridade) VALUES (%s, %s, %s, %s, %s, %s);"
    #     values = (idOrdemManutencao, data, descricao, local, blob, prioridade)
    #     cursor.execute(SQL, values)
    #     connection.commit()

    #     cursor.close()
    #     connection.close()

    #     flash('Editado com sucesso!', 'sucess')
    #     return render_template('index1.html')

    # else:
    # return render_template('editar_pedido.html')

# Rota para o INDEX 2
@app.route('/index2')
def index2 ():

    # Faz a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Monta a instrução SQL de seleção
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade FROM ordem_manutencao WHERE ativo = 1;"

    # Executa a consulta SQL
    cursor.execute(SQL)

    # Cria um vetor com os resultados da consulta 
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    #Renderizar
    return render_template('index2.html', ordens=ordens)

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
        return redirect(url_for('index2'))
        # return render_template('index2.html')

    else:
        return render_template('fazer_pedido.html')

# Rota para o INDEX 3
@app.route('/index3')
def index3 (): #função de visualização

    # Faz a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Monta a instrução SQL de seleção
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade, status FROM ordem_manutencao WHERE ativo = 1;"

    # Executa a consulta SQL
    cursor.execute(SQL)

    # Cria um vetor com os resultados da consulta 
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    connection.close()

    todas_ordens = []

    # Calcula a situação de cada empréstimo
    for ordem in ordens:

        # Recupera as informações de data
        prioridade = ordem[4]

        # Verifica se o empréstimo está em dia ou atrasado
        if (prioridade == 0): categoria = "Não definida"
        if (prioridade == 1): categoria = "Alta"
        if (prioridade == 2): categoria = "Média"
        if (prioridade == 3): categoria = "Baixa"

        # Converte cada linha do banco de dados para lista
        ordem_atual = list(ordem)
        ordem_atual.append(categoria)

        # Adiciona o empréstimo atualizado na lista com todos os empréstimos
        todas_ordens.append(ordem_atual)

    # Calcula a situação de cada empréstimo
    for ordem in ordens:

        # Recupera as informações de data
        status = ordem[5]

        # Verifica se o empréstimo está em dia ou atrasado
        if (status == 0): categoria = "Não iniciada"
        if (status == 1): categoria = "Em andamento"
        if (status == 2): categoria = "Concluída"

        # Converte cada linha do banco de dados para lista
        ordem_atual = list(ordem)
        ordem_atual.append(categoria)

        # Adiciona o empréstimo atualizado na lista com todos os empréstimos
        todas_ordens.append(ordem_atual)  

    #Renderizar
    return render_template('index3.html', ordens=todas_ordens)

# Rota para o EDITAR PEDIDO
@app.route('/abrir-pedido', methods=['POST'])
@app.route('/abrir-pedido/<idOrdemManutencao>', methods=['GET'])
def abrir_pedido(idOrdemManutencao=None):

    # Verifica se o método da requisição é o POST
    if(request.method == 'POST'):

        # Recebe os dados do formulário via POST
        idOrdemManutencao = request.form['idOrdemManutencao']
        status = request.form['status']

        # Faz conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL para atualizar os dados do leitor
        SQL = "UPDATE ordem_manutencao SET status = %s WHERE idOrdemManutencao = %s;"
        values = (status, idOrdemManutencao)
        print(SQL)
        print(f'Esse é o ID {idOrdemManutencao}, essa é a status {status}')
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Redireciona para a página de listagem de leitores
        return redirect(url_for('index3'))
    else:
        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL para selecionar o leitor com base no CPF
        SQL = "SELECT idOrdemManutencao, data, descricao, local, imagem, status FROM ordem_manutencao WHERE idOrdemManutencao = %s;"
        
        # SQL = "SELECT data, descricao, local, imagem, status FROM ordem_manutencao;"
        cursor.execute(SQL, (idOrdemManutencao,))
        ordem = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Verifica se a imagem existe e converte para um formato que o HTML pode usar
        imagem_base64 = None
        if ordem[4]:
            imagem_base64 = base64.b64encode(ordem[4]).decode('utf-8')
            imagem_base64 = f"data:image/jpeg;base64,{imagem_base64}"

        # Retorna a página HTML de edição do leitor com os dados preenchidos
        return render_template('abrir_pedido.html', ordem=ordem, imagem=imagem_base64)

#IMAGEM
# def get_image_from_db(image_id):
#     # Função para recuperar a imagem do banco de dados usando o ID fornecido
#     # Conecta ao banco de dados
#     conn = sqlite3.connect('seu_banco_de_dados.db')
#     cursor = conn.cursor()
    
#     # Executa uma consulta SQL para buscar a imagem
#     cursor.execute("SELECT imagem FROM sua_tabela WHERE id = ?", (image_id,))
#     image_blob = cursor.fetchone()  # Pega o resultado da consulta
    
#     conn.close()  # Fecha a conexão com o banco de dados
    
#     # Retorna o Blob da imagem se encontrado, senão retorna None
#     if image_blob:
#         return image_blob[0]  # Retorna o Blob da imagem
#     return None

# @app.route('/imagem/<int:image_id>', methods=['GET'])
# def imagem(image_id):
#     # Rota para buscar e retornar a imagem pelo ID
#     image_data = get_image_from_db(image_id)  # Chama a função para obter a imagem
    
#     # Verifica se a imagem foi encontrada
#     if image_data:
#         # Retorna a imagem como um arquivo para o navegador
#         return send_file(
#             io.BytesIO(image_data),  # Converte o Blob em um stream de bytes
#             mimetype='image/jpeg'  # Define o tipo MIME da imagem (altere conforme necessário)
#         )
#     else:
#         abort(404)  # Se a imagem não foi encontrada, retorna um erro 404

#!Não trazer para cima:

# Execução do aplicativo da web
if __name__ == '__main__':
    app.run(debug=True)