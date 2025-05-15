from django.shortcuts import render, redirect
from main.bd_config import conecta_no_banco_de_dados
from .forms import ContatoForm
from .decorators import validate_login
from django.shortcuts import render, redirect
from .forms import ContatoForm  
from .bd_config import conecta_no_banco_de_dados


def index(request):
    return render(request, 'Guia/index.html')

def sobre(request):
    return render(request, 'Sobre/sobre.html')

@validate_login
def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                bd = conecta_no_banco_de_dados()
                nome = form.cleaned_data['nome']
                email = form.cleaned_data['email']
                mensagem = form.cleaned_data['mensagem']
                sql = "INSERT INTO contatos (nome, email, mensagem) VALUES (%s, %s, %s)"
                values = (nome, email, mensagem)
                cursor = bd.cursor()
                cursor.execute(sql, values)
                bd.commit()
                print(f"Dados do formulário salvos com sucesso!")
                return HttpResponseRedirect('/')
            except Exception as err:
                print(f"Erro ao salvar dados no banco de dados: {err}")
                mensagem_erro = "Ocorreu um erro ao processar o seu contato. Tente novamente mais tarde."
                return render(request, 'erro.html', {'mensagem_erro': mensagem_erro})
            finally:
                if bd is not None:
                    bd.close()
        else:
            return render(request, 'contato.html', {'form': form})
    else:
        form = ContatoForm()
        return render(request, 'contato.html', {'form': form})

def login(request):
    request.session['usuario_id'] = ""
    if request.method == 'POST':
        try:
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            nome = request.POST['nome']
            senha = request.POST['senha']
            email = request.POST['email']
            
            cursor.execute("""
                SELECT *
                FROM usuarios
                WHERE email = %s AND senha = %s;
            """, (email, senha))
            usuario = cursor.fetchone()
            
            if usuario:
                request.session['usuario_id'] = usuario[0]
                return redirect('apostar')  
            else:
                mensagem_erro = 'Email ou senha inválidos.'
                return render(request, 'Login/login.html', {'mensagem_erro': mensagem_erro})
        except Exception as e:
            mensagem_erro = f"Erro ao conectar ao banco de dados: {e}"
            return render(request, 'Login/login.html', {'mensagem_erro': mensagem_erro})
        finally:
            cursor.close()
            bd.close()
    return render(request, 'Login/login.html')

def cadastrar(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        
        if not all([nome, email, senha]):
            mensagem_erro = 'Todos os campos são obrigatórios.'
            return render(request, 'Cadastrar/cadastrar.html', {'mensagem_erro': mensagem_erro})

        try:
            
            bd = conecta_no_banco_de_dados()
            cursor = bd.cursor()
            sql = """
                INSERT INTO usuarios (nome, email, senha)
                VALUES (%s, %s, %s);
            """
            valores = (nome, email, senha)
            cursor.execute(sql, valores)
            bd.commit()
            cursor.close()
            bd.close()
            
            request.session['usuario_id'] = cursor.lastrowid 
            return redirect('apostar')  
        except Exception as e:
            mensagem_erro = f"Erro ao cadastrar usuário: {e}"
            return render(request, 'Cadastrar/cadastrar.html', {'mensagem_erro': mensagem_erro})
    else:
    
        return render(request, 'Cadastrar/cadastrar.html')


@validate_login
def atualizarUsuario(request, id):
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()
    cursor.execute("""
        SELECT id, nome, email
        FROM usuarios
        WHERE id = %s;
    """, (id,))
    dados_usuario = cursor.fetchone()
    cursor.close()
    bd.close()
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        if not all([nome, email, senha]):
            return render(request, 'AtualizarUsuario/atualizarUsuario.html', {'id': id})
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        sql = "UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE id = %s"
        values = (nome, email, senha, id)
        cursor.execute(sql, values)
        bd.commit()
        cursor.close()
        bd.close()
        return redirect('sobre')
    return render(request, 'AtualizarUsuario/atualizarUsuario.html', {'id': id, 'dados_usuario': dados_usuario})

@validate_login
def logout(request):
    request.session.flush()
    return redirect('login')
@validate_login
@validate_login
def apostar(request):
    try:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()
        
        cursor.execute("SELECT id, nome FROM usuarios")
        usuarios = cursor.fetchall()
        
        if len(usuarios) < 2:
            mensagem_erro = "Não há usuários suficientes para realizar uma aposta."
            return render(request, 'apostar.html', {'mensagem_erro': mensagem_erro})
        
        import random
        
        jogador1, jogador2 = random.sample(usuarios, 2)
        
        
        vencedor = random.choice([jogador1, jogador2])
        perdedor = jogador1 if vencedor == jogador2 else jogador2
        
       
        resultado = {
            'vencedor': {'id': vencedor[0], 'nome': vencedor[1]},
            'perdedor': {'id': perdedor[0], 'nome': perdedor[1]},
        }

        return render(request, 'apostar.html', {'resultado': resultado})
    
    except Exception as e:
        mensagem_erro = f"Erro ao acessar o banco de dados: {e}"
        return render(request, 'apostar.html', {'mensagem_erro': mensagem_erro})
    
    finally:
        if bd is not None:
            bd.close()


def registrar_resultado(contato_id, resultado):
    try:
        bd = conecta_no_banco_de_dados()
        cursor = bd.cursor()

        if resultado == 'vitoria':
            cursor.execute('UPDATE placar SET vitorias = vitorias + 1 WHERE contatos = %s;', (contato_id,))
        elif resultado == 'derrota':
            cursor.execute('UPDATE placar SET derrotas = derrotas + 1 WHERE contatos = %s;', (contato_id,))
        else:
            raise ValueError('Resultado inválido.')

        bd.commit()
        cursor.close()

    except mysql.connector.Error as err:
        print("Erro ao atualizar placar:", err)
    finally:
        if bd is not None:
            bd.close()

@validate_login
def atualizar_usuario(request, id):
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()
    
    
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    
    if not usuario:
        return HttpResponse("Usuário não encontrado.", status=404)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha', '')  

        
        cursor.execute("""
            UPDATE usuarios 
            SET nome = %s, email = %s, senha = %s
            WHERE id = %s
        """, (nome, email, senha, id))
        bd.commit()
        cursor.close()
        bd.close()
        return redirect('sobre')  

    cursor.close()
    bd.close()
    return render(request, 'AtualizarUsuario/atualizarUsuario.html', {'usuario': usuario})



@validate_login
def deletar_usuario(request, id):
    bd = conecta_no_banco_de_dados()
    cursor = bd.cursor()

    
    cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        return HttpResponse("Usuário não encontrado.", status=404)

    
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    bd.commit()
    cursor.close()
    bd.close()

    return redirect('sobre')  