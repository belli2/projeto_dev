#Importação das bibliotecas e módulos

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
# from datetime import datetime
import resources.database_connection as database_connection

#Configuração do aplicativo da web

app = Flask(__name__)

#Chave de proteção contra CSRF (Cross-Site Request Forgery)

app.config['SECRET_KEY'] = 'manutenc@oTCC'

#Rota para o index

@app.route('/')
def login ():

    #Renderizar a página inicial
    return render_template('login.html')

#Rota para o cadastro

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

        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL e insere os dados no banco de dados
        SQL = "INSERT INTO usuarios (nome, cpf, email, senha, nivel_acesso) VALUES (%s, %s, %s, %s, %s);"
        values = (nome, cpf, email, senha, nivel_acesso)
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Redireciona o usuário após cadastro dos dados no Banco de Dados
        return redirect(url_for('login'))

    else:
        return render_template('cadastro.html')

#Rota para o esqueci a senha

@app.route('/esqueci-senha')
def esqueci_senha ():

    #Renderizar
    return render_template('esqueci_senha.html')

#Rota para o index 1

@app.route('/index1')
def index1 ():

    #Renderizar
    return render_template('index1.html')

#Rota para o index 2

@app.route('/index2')
def index2 ():

    #Renderizar
    return render_template('index2.html')

#Rota para o index 3

@app.route('/index3')
def index3 ():

    #Renderizar
    return render_template('index3.html')

#!Não trazer para cima:

#Execução do aplicativo da web

if __name__ == '__main__':
    app.run(debug=True)