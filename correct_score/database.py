import mysql.connector
from dotenv import load_dotenv
from os import getenv
from sqlalchemy import create_engine,text
import urllib.parse

load_dotenv()

def db_mysql():
    host = getenv('HOST_DATABASE')
    user = getenv('USER_DATABASE')
    password = getenv('PASSWORD_DATABASE')
    database = getenv('TABLE_DATABASE')
    password = urllib.parse.quote_plus(password)
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    return engine


def database(comando):
    """
    params:
    comando => 'Select, Insert or Update' : STR or List
    """
    engine = db_mysql()
    with engine.begin() as c:
        if 'SELECT' in comando:
            resultado = c.execute(text(comando)).fetchall()
            c.close()
            return resultado

        if type(comando) == list:
            for um_comando in comando:
                c.execute(text(um_comando))
        else:
            c.execute(text(comando))
            
    # conexao = mysql.connector.connect(
    #     host = getenv('HOST_DATABASE'),
    #     user = getenv('USER_DATABASE'),
    #     password = getenv('PASSWORD_DATABASE'),
    #     database = getenv('TABLE_DATABASE')
    # )
    # cursor = conexao.cursor()
    # try:
    #     if 'SELECT' in comando:
    #         cursor.execute(comando)
    #         resultado = cursor.fetchall() # ex de resultado: [(1.29, 30)]
    #         cursor.close()
    #         conexao.close
    #         return resultado

    #     if type(comando) == list:
    #         for c in comando:
    #             cursor.execute(c)
    #     else:
    #         cursor.execute(comando)
    # except:
    #     print('erro no DATABASE, fechando conexão')
    # finally:
    #     conexao.commit()
    #     cursor.close()
    #     conexao.close

def delete_database(table, url):
    """
    deleta jogos q nao serão mais analisados do banco de dados jogos do dia
    params => url: str
    """
    # conexao = mysql.connector.connect(
    #     host = getenv('HOST_DATABASE'),
    #     user = getenv('USER_DATABASE'),
    #     password = getenv('PASSWORD_DATABASE'),
    #     database = getenv('TABLE_DATABASE')
    # )
    # cursor = conexao.cursor()

    # cursor.execute(f'DELETE FROM {table} WHERE (`url` = "{url}");')
    # conexao.commit()

    # cursor.close()
    # conexao.close
    engine = db_mysql()
    with engine.begin() as c:
        c.execute(text(f'DELETE FROM {table} WHERE (`url` = "{url}");'))

# def fecha_conexao():
    # conexao = mysql.connector.connect(
    #     host = getenv('HOST_DATABASE'),
    #     user = getenv('USER_DATABASE'),
    #     password = getenv('PASSWORD_DATABASE'),
    #     database = getenv('TABLE_DATABASE')
    # )
    # cursor = conexao.cursor()

    # cursor.close()
    # conexao.close
