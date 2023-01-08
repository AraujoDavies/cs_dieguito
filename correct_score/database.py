import mysql.connector
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def database(comando):
    """
    params:
    comando => 'Select, Insert or Update' : STR or List
    """
    conexao = mysql.connector.connect(
        host = getenv('HOST_DATABASE'),
        user = getenv('USER_DATABASE'),
        password = getenv('PASSWORD_DATABASE'),
        database = getenv('TABLE_DATABASE')
    )
    cursor = conexao.cursor()
    try:
        if 'SELECT' in comando:
            cursor.execute(comando)
            resultado = cursor.fetchall() # ex de resultado: [(1.29, 30)]
            cursor.close()
            conexao.close
            return resultado

        if type(comando) == list:
            for c in comando:
                cursor.execute(c)
        else:
            cursor.execute(comando)
    except:
        print('erro no DATABASE, fechando conexão')
    finally:
        conexao.commit()
        cursor.close()
        conexao.close

def delete_database(table, url):
    """
    deleta jogos q nao serão mais analisados do banco de dados jogos do dia
    params => url: str
    """
    conexao = mysql.connector.connect(
        host = getenv('HOST_DATABASE'),
        user = getenv('USER_DATABASE'),
        password = getenv('PASSWORD_DATABASE'),
        database = getenv('TABLE_DATABASE')
    )
    cursor = conexao.cursor()

    cursor.execute(f'DELETE FROM {table} WHERE (`url` = "{url}");')
    conexao.commit()

    cursor.close()
    conexao.close

def fecha_conexao():
    conexao = mysql.connector.connect(
        host = getenv('HOST_DATABASE'),
        user = getenv('USER_DATABASE'),
        password = getenv('PASSWORD_DATABASE'),
        database = getenv('TABLE_DATABASE')
    )
    cursor = conexao.cursor()

    cursor.close()
    conexao.close