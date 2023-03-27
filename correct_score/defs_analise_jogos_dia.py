# entrar nos links e pegar eventos nao iniciados
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from database import database, delete_database
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta
from telegram import enviar_no_telegram
from helpers import time_game_start
import logging

load_dotenv()

def gap_and_odd(driver, x):
    """
        Verifica GAP do mercado e retorna odd do back e do lay como float
        params: 
        6: int (se entrada no 1-2)
        9: int (se entrada no 2-1)
    """
    sleep(5)
    resultado = driver.find_element('xpath', '//bf-marketview-runners-list[@class="runners-list-unpinned"]').get_attribute('innerHTML')
    soup = BeautifulSoup(resultado, "html.parser")
    resultados = soup.find_all('tr', class_ = 'runner-line')

    back = resultados[x].find('td', class_='last-back-cell').text 
    odd_back = float(back.split()[0])
    valor_correspondido_back = back.split()[1]

    lay = resultados[x].find('td', class_='first-lay-cell').text 
    odd_lay = float(lay.split()[0])
    valor_correspondido_lay = lay.split()[1]

    gap = odd_lay - odd_back

    if gap > 0.8: # se gap mto alto
        logging.warning(f"GAP superior a 3 ticks: Back: @{odd_back} | Lay: @{odd_lay}")

    return [odd_back, odd_lay, gap]

def notifica_ajustedb(driver, odd_lay, x, equipes, url, placar, favorito, competicao, tempo_de_jogo):
    """
        Notifica no telegram, ajusta database e faz entrada(propoe) na traderbet
        params:
            driver
            odd_lay: float | x: int (x/19 mercados) | demais parametros vem do looping do DB
    """
    url_betfair = driver.current_url
    id_evento = url_betfair.split('/')[-1]
    url_bolsa_apostas = f'https://bolsadeaposta.com/exchange/sport/market/{id_evento}'
    url_trader_bet = f'https://www.tradexbr.com/customer/sport/market/{id_evento}'
    sair_em = 85 - int(tempo_de_jogo)
    data_saida = datetime.now() + timedelta(minutes=sair_em)
    # notificar no telegram
    msg = f"""
⚽️⚠️<b>{equipes}</b> {tempo_de_jogo}'

📚🎯<b>Entrada: </b>{'Lay 1 - 2' if x == 6 else 'Lay 2 - 1'} até o HT
🎲🥅ODD: {odd_lay} 🚨 ODD Máx.: 13

🚨 <b>Saída: </b> 70 ~ 75 Min. **caso entrada não seja concluída
⏰ {data_saida.strftime("%H:%M")} (17H27 horário de brasília)
"""
    logging.warning(msg)
    enviar_no_telegram(getenv('TELEGRAM_CHAT_ID'), msg)

    # deletar do database de analise e passa para o database de entradas em andamento
    comando = f'INSERT INTO {getenv("TABLE_ENTRADAS_EM_ANDAMENTO")} (`jogo`, `placar`, `competicao`, `odd_entrada`, `favorito`, `url`) VALUES ("{equipes}", "{placar}", "{competicao}", "{odd_lay}", "{favorito}", "{url_betfair}")'
    database(comando)
    delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)


def analise_jogos_do_dia(driver, jogos_do_dia):
    """Recebe dados do banco e analisa em busca de padrão."""
    jogos_em_andamento = 0
    for evento in jogos_do_dia:
        try:
            event_start = evento[5] # data de inicio do jogo
            # se jogo já iniciou...
            if event_start != None:
                if datetime.now() > event_start: 
                    jogos_em_andamento += 1
                    equipes = evento[1]
                    # logging.warning(evento)
                    favorito = evento[2] # 0(home) 1(away)
                    competicao = evento[6]
                    vezes_q_foi_adiado = evento[8]
                    url = evento[7]

                    logging.warning(f'{equipes} mandante é fav' if favorito == 0 else f'{equipes} visitante é fav')
                    
                    driver.get(url)
                    driver.implicitly_wait(5)

                    # deleta jogo do banco se url nao encontrada
                    pagina_indisponivel = driver.find_elements('xpath', '//h2[@class="title"]')
                    if bool(pagina_indisponivel):
                        delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                        logging.warning(f'Página indispónivel p o jogo: {evento[1]}')
                        continue
                    
                    try:
                        WebDriverWait(driver, 20, 3).until(lambda x: x.find_element('xpath', '//*[@class="star-favourites"]'))
                    except:
                        # evitar erro se tomar timeout
                        continue

                    # se o jogo ainda nao iniciou, att datetime 
                    date = driver.find_elements('xpath', '//div[@class="date"]')
                    if bool(date): 
                        h = datetime.now().hour
                        min = datetime.now().minute
                        if min < 55:
                            min += 5
                        else:
                            min = 5
                            h += 1
                        tempo_in_datetime = time_game_start(int(h), int(min))
                        comando = f'UPDATE {getenv("TABLE_JOGOS_DO_DIA")} SET `data_inicio` = "{tempo_in_datetime}", `foi_adiado` = "{vezes_q_foi_adiado + 1}" WHERE (`url` = "{url}")'
                        database(comando)
                        logging.warning(f'jogo {equipes} nao iniciou no horário previsto! adiando datetime')
                        # deleta jogo do banco se já adiou mais de 10 vezes
                        if vezes_q_foi_adiado > 10: 
                            database(f'DELETE FROM {getenv("TABLE_JOGOS_DO_DIA")} WHERE (`url` = "{url}")')
                        continue

                    # verificar se favorito perde por 1 a 0
                    placar = driver.find_elements('xpath', '//span[@class="score"]')
                    if bool(placar) and placar[0].text != '':
                        placar = placar[0].text
                        placar_home = int(placar.split('-')[0])
                        placar_away = int(placar.split('-')[1])
                        # se favorito saiu ganhando deleta
                        if favorito == 0 and placar_home == 1 or favorito == 1 and placar_away == 1:
                            logging.warning('Favorito já marcou, removendo jogo.')
                            delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                        # se já saiu mais de 1 gol
                        if placar_home > 1 or placar_away > 1:
                            logging.warning('Já saiu mais de 1 gol... removendo jogo.')
                            delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                    # se jogo iniciado mas sem placar
                    else:
                        delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                        logging.warning(f'O jogo: {evento[1]}, Não exibe placar (excluido das análises)')
                        continue
                    logging.warning(f'{placar_home} X {placar_away}')

                    # deleta do banco dos jogos do dia se tempo superior a 34 (Perda de Padrão) ou se igual a intervalo
                    tempo = driver.find_elements('xpath', '//p[@class="time-elapsed inplay"]')
                    tempo = tempo[0].text
                    if tempo != 'Intervalo':
                        tempo = int(tempo.split("'")[0])
                        if tempo > 34:
                            delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                            logging.warning(f'jogo não será mais observado (+35min): {evento[1]}')
                            continue
                    else:
                        delete_database(getenv("TABLE_JOGOS_DO_DIA"), url)
                        logging.warning(f'jogo não será mais observado (+35min): {evento[1]}')
                        continue
                    logging.warning(f'tempo de jogo: {tempo}')

                    # abre o mercado de resultado correto
                    mercados = driver.find_elements('xpath', '//a[@link-type="MARKET"]')
                    for market in mercados:
                        if 'Resultado correto' in market.text:
                            market.click()
                            break

                    # Verificar liquidez
                    try:
                        liquidez = driver.find_element('xpath', '//span[@class="total-matched"]').text
                        liquidez_tratada = float(liquidez.split()[-1].replace(',', ''))
                        if liquidez_tratada > 30000:
                            logging.warning('Liquidez acima de 30k')
                            # verificar gap do mercado e odd do 2x1 ou 1x2 dependendo do fator casa
                            if favorito == 0 and placar_home == 0 and placar_away == 1: # favorito perdendo em casa (0x1)
                                logging.warning('padrão encontrado no favorito jogando EM CASA')
                                odd_back, odd_lay, gap = gap_and_odd(driver, 6)
                                # odd entre 5.8 e 10.5 e gap inferior a 4 ticks
                                if odd_lay > 5.8 and odd_lay <= 12.5 and gap < 0.8:
                                    notifica_ajustedb(driver, odd_lay, 6, equipes, url, placar, favorito, competicao, tempo)
                            elif favorito == 1 and placar_home == 1 and placar_away == 0: # favorito perdendo fora (1x0)
                                logging.warning('padrão encontrado no favorito jogando FORA')
                                odd_back, odd_lay, gap = gap_and_odd(driver, 9)
                                # odd entre 5.8 e 10.5 e gap inferior a 4 ticks
                                if odd_lay > 5.8 and odd_lay <= 12.5 and gap < 0.8:
                                    notifica_ajustedb(driver, odd_lay, 9, equipes, url, placar, favorito, competicao, tempo)
                            else:
                                logging.warning('NADA DE PADRÃO')
                        else:
                            logging.warning(f'({liquidez_tratada})Liquidez abaixo de 30k')
                    except:
                        logging.warning('LIQUIDEZ FALHOU!')
        except:
            logging.error(f"Falha no evento: {evento}")
            print(f"Falha no evento: {evento}")
            sleep(10)

    logging.warning(f'jogos analisados: {jogos_em_andamento}')
    # tempo de sleep do código para próxima analise
    return jogos_em_andamento