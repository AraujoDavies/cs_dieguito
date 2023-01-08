from time import sleep
from database import database
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
import logging

load_dotenv()

# filtrar odds e armazenar em um database jogos onde há um favorito abaixo de 2.10
def jogos_selecionados(jogos_para_analisar):
    """
        - Salva jogos selecionados(odd < 2.22) no banco de dados

        - diz quem é o Favorito
        
        params
        jogos_para_analsar: lista com vários dicts
    """
    for evento in jogos_para_analisar:
        favorito = None
        jogo = f'{evento["mandante"]} X {evento["visitante"]}'
        odd_mandante = float(evento['odd_back_mandante'])
        odd_visitante = float(evento['odd_back_visitante'])
        url = evento['url']
        competicao = evento['competicao']
        if odd_mandante < 2.22:
            favorito = 0 # 0(home) ou 1(away)
        if odd_visitante < 2.22:
            favorito = 1
        # logging.warning(jogo, odd_mandante, odd_visitante, url, competicao, favorito)

        comando = f'SELECT url FROM {getenv("TABLE_JOGOS_DO_DIA")} WHERE url = "{url}";'
        urls_ja_analisadas = database(comando)

        if favorito != None and bool(urls_ja_analisadas) == False: # se existe um favorito E nao está no banco de dados
            logging.warning(f"favorito: {favorito}; jogo:{jogo}; odd_mandante: {odd_mandante}; odd_visitante: {odd_visitante}; url: {url}; competicao: {competicao}")
            comando = f'INSERT INTO {getenv("TABLE_JOGOS_DO_DIA")} (`jogo`, `favorito`, `odd_mandante`, `odd_visitante`, `url`, `competicao`) VALUES ("{jogo}", "{favorito}", "{odd_mandante}", "{odd_visitante}","{url}", "{competicao}")'
            database(comando)

def time_game_start(h, min):
    """
    cria datetime com o horário solicitado nos parâmetros
    params:
    h = horário de inicio : int
    min = minuto de iinicio : int
    """
    y = datetime.now().year
    m = datetime.now().month
    d = datetime.now().day
    # h = datetime.now().hour
    # min = datetime.now().minute
    # s = datetime.now().second
    return datetime(year=y, month=m, day=d, hour=h, minute=min)
    
def data_inicio(driver):
    """
    Att o campo data de inicio no database. deve ser executada logo após finalizar a filtragem dos jogos
    """
    comando = f'SELECT url, data_inicio FROM {getenv("TABLE_JOGOS_DO_DIA")};'
    jogos = database(comando)

    for select in jogos:
        url = select[0]
        data_inicio = select[1]
        if data_inicio == None: # se não foi atribuida nenhuma data
            driver.get(url)
            sleep(5)
            date = driver.find_elements('xpath', '//div[@class="date"]')
            # armazena no DATABASE os horarios de inicio se encontrar o horario
            if bool(date):
                data = date[0].text
                horas, min = data.split(', ')[1].split(':')
                tempo_in_datetime = time_game_start(int(horas), int(min))
                comando = f'UPDATE {getenv("TABLE_JOGOS_DO_DIA")} SET data_inicio = "{tempo_in_datetime}" WHERE url = "{url}";'
                database(comando)
            # se pegar um jogo já iniciado
            else: 
                h = datetime.now().hour
                min = datetime.now().minute
                tempo_in_datetime = time_game_start(h, min)
                comando = f'UPDATE {getenv("TABLE_JOGOS_DO_DIA")} SET data_inicio = "{tempo_in_datetime}" WHERE url = "{url}";'
                database(comando)