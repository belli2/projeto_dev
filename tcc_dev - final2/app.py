# Importação das bibliotecas
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
import base64
from datetime import datetime
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
        session['idUsuarios'] = usuario[0]

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
    

# Rota para o CADASTRO.
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    # Verifica se existe alguma requisição via POST
    if request.method == 'POST':

        # Recupera os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        nivel_acesso = request.form['nivel_acesso']
        numero_telefone = request.form['numero_telefone']
        cidade = request.form['cidade']

        # Conecta ao banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Verificar se o CPF já está cadastrado.
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cpf = %s;", (cpf,))
        if cursor.fetchone()[0] > 0:
            flash('CPF já cadastrado...', 'error')
            cursor.close()
            connection.close()
            return render_template('cadastro.html')

        # Verificar se o em-ail já está cadastrado.
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s;", (email,))
        if cursor.fetchone()[0] > 0:
            flash('E-mail já cadastrado...', 'error')
            cursor.close()
            connection.close()
            return render_template('cadastro.html')

        # Verificar se o número de telefone já está cadastrado.
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE numero_telefone = %s;", (numero_telefone,))
        if cursor.fetchone()[0] > 0:
            flash('Número de telefone já cadastrado...', 'error')
            cursor.close()
            connection.close()
            return render_template('cadastro.html')

        # Criptografa a senha do usuário.
        senha = hashlib.sha256(senha.encode('utf-8')).hexdigest()

        # Monta a instrução SQL e insere os dados no banco de dados.
        SQL = "INSERT INTO usuarios (nome, cpf, email, senha, nivel_acesso, numero_telefone, cidade) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        values = (nome, cpf, email, senha, nivel_acesso, numero_telefone, cidade)
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados.
        cursor.close()
        connection.close()

        # Redireciona o usuário após cadastro dos dados no Banco de Dados.
        flash('Cadastro realizado com sucesso!!!', 'success')
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
            return redirect(url_for('mudar_senha', user_id=perguntas[0]))
        else:
            flash('Dados incorretos...', 'error')
            return redirect(url_for('login'))

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
        connection.commit()

        # Verifica se há erro
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
def index1():
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Filtrar status
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade FROM ordem_manutencao WHERE ativo = 1 AND status != 2;"

    cursor.execute(SQL)
    ordens = cursor.fetchall()

    cursor.close()
    connection.close()

    # Função para formatar data
    def formata_data(data):

        # Verifica se a data existe 
        if (data):
            data_formatada = datetime.strptime(str(data), '%Y-%m-%d').strftime('%d/%m/%Y')
            return (data_formatada)
        
        return (data)

    # Aplique a formatação da data
    ordens_formatadas = [
        (ordem[0], formata_data(ordem[1]), ordem[2], ordem[3], ordem[4])
        for ordem in ordens
    ]

    todas_ordens = []

    for ordem in ordens_formatadas:
        prioridade = ordem[4]
        categoria = "Não definida" if prioridade == 0 else "Alta" if prioridade == 1 else "Média" if prioridade == 2 else "Baixa"
        
        # Constrói uma nova lista com a ordem e a categoria
        ordem_atual = list(ordem)  # Cria uma cópia da ordem para adicionar a categoria
        ordem_atual.append(categoria)
        todas_ordens.append(ordem_atual)

    # Ordena a lista de ordens com base na prioridade, considerando: Alta > Média > Baixa > Não definida
    todas_ordens = sorted(todas_ordens, key=lambda x: x[4])

    return render_template('index1.html', ordens=todas_ordens)

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

        # Redirecionar
        return redirect(url_for('index1'))

    else:

        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL
        SQL = "SELECT idOrdemManutencao, data, descricao, local, imagem, prioridade FROM ordem_manutencao WHERE idOrdemManutencao = %s;"
        
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


# Rota para o INDEX 2
@app.route('/index2')
def index2():

    # Abre a conexão com o banco de dados
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Query para selecionar ordens de manutenção.
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade FROM ordem_manutencao WHERE ativo = 1 AND status != 2;"
    
    # Executa a consulta e pega os dados.
    cursor.execute(SQL)
    ordens = cursor.fetchall()

    # Função para formatar data
    def formata_data(data):

        # Verifica se a data existe. 
        if (data):
            data_formatada = datetime.strptime(str(data), '%Y-%m-%d').strftime('%d/%m/%Y')
            return (data_formatada)
        
        return (data)

    # Formatação da data
    ordens_formatadas = [
        (ordem[0], formata_data(ordem[1]), ordem[2], ordem[3], ordem[4])
        for ordem in ordens
    ]

    # Encerra a conexão com o banco de dados.
    cursor.close()
    connection.close()

    # Renderiza o template e passa para ele as ordens de serviço.
    return render_template('index2.html', ordens=ordens_formatadas)

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
        idUsuarios = session.get('idUsuarios')

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

    else:
        return render_template('fazer_pedido.html')

# Rota para o INDEX 3
@app.route('/index3')
def index3():

    # Abre a conexão com o banco de dados.
    connection = database_connection.open_connection()
    cursor = connection.cursor()

    # Seleciona os dados das ordens de serviço que não foram concluidas.
    SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade, status FROM ordem_manutencao WHERE ativo = 1 AND status != 2;"
    cursor.execute(SQL)
    ordens = cursor.fetchall()

    # Fecha a conexão com o banco de dados.
    cursor.close()
    connection.close()

    # Função para formatar data
    def formata_data(data):

        # Verifica se a data existe. 
        if (data):
            data_formatada = datetime.strptime(str(data), '%Y-%m-%d').strftime('%d/%m/%Y')
            return (data_formatada)
        
        return (data)

    # Formatação da data
    ordens_formatadas = [
        (ordem[0], formata_data(ordem[1]), ordem[2], ordem[3], ordem[4], ordem[5])
        for ordem in ordens
    ]


    # Lista com as ordens categorizadas.
    ordens_categorizadas = []

    # Dicionário de categorização das ordens.
    prioridades = {0: "Não definida", 1: "Alta", 2: "Média", 3: "Baixa"}
    status_tipos = {0: "Não iniciada", 1: "Em andamento", 2: "Concluída"}

    # Percorre cada ordem retornada do banco de dados.
    for ordem in ordens_formatadas:

        # Classifica a prioridade e o status da ordem.
        prioridade_texto = prioridades.get(ordem[4], "Desconhecida")
        status_texto = status_tipos.get(ordem[5], "Desconhecido")

        # Recupera todos os valores da ordem atual.
        ordem_atualizada = list(ordem)

        # Substitui os valores da prioridade e do status pela categoria.
        ordem_atualizada[4] = prioridade_texto
        ordem_atualizada[5] = status_texto
        
        # Cria uma nova lista com as ordens categorizadas.
        ordens_categorizadas.append(ordem_atualizada)

    # Define os níveis de ordenação (prioridade e status).
    prioridade_niveis = {"Alta": 1, "Média": 2, "Baixa": 3, "Não definida": 4}
    status_niveis = {"Em andamento": 1, "Não iniciada": 2}

    # Faz a ordenação.
    ordens_categorizadas.sort(key=lambda x: (prioridade_niveis.get(x[4], 5), status_niveis.get(x[5], 3)))

    # Renderiza o template e passa para ele a lista com as ordens categorizadas.
    return render_template('index3.html', ordens=ordens_categorizadas)

# Rota para o ABRIR PEDIDO
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

        # Monta a instrução SQL para atualizar
        SQL = "UPDATE ordem_manutencao SET status = %s WHERE idOrdemManutencao = %s;"
        values = (status, idOrdemManutencao)
        print(SQL)
        print(f'Esse é o ID {idOrdemManutencao}, essa é a status {status}')
        cursor.execute(SQL, values)
        connection.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Redirecionar
        return redirect(url_for('index3'))

    else:

        # Faz a conexão com o banco de dados
        connection = database_connection.open_connection()
        cursor = connection.cursor()

        # Monta a instrução SQL para selecionar o leitor com base no CPF
        SQL = "SELECT idOrdemManutencao, data, descricao, local, prioridade, imagem, status FROM ordem_manutencao WHERE idOrdemManutencao = %s;"
        
        cursor.execute(SQL, (idOrdemManutencao,))
        ordem = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        connection.close()

        # Verifica se a imagem existe e converte para um formato que o HTML pode usar
        imagem_base64 = None
        if ordem[5]:
            imagem_base64 = base64.b64encode(ordem[5]).decode('utf-8')
            imagem_base64 = f"data:image/jpeg;base64,{imagem_base64}"

        # Retorna a página HTML de edição do leitor com os dados preenchidos
        return render_template('abrir_pedido.html', ordem=ordem, imagem=imagem_base64)
    
#!Não trazer para cima:

# Execução do aplicativo da web
if __name__ == '__main__':
    app.run(debug=True)