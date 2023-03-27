from database import database, delete_database
from dotenv import load_dotenv
from os import getenv
from selenium.webdriver.support.ui import WebDriverWait
from defs_analise_jogos_dia import gap_and_odd
from telegram import resultado_da_entrada, app
import logging
from datetime import datetime

load_dotenv()


def entrada_concluido(driver, favorito):
    """
        retorna true se o placar for de entrada concluida e false caso contrário
        params:
            driver
            favorito: int | 0 to home, 1 to away
    """
    placar = driver.find_elements('xpath', '//span[@class="score"]')
    url = driver.current_url

    if bool(placar):
        placar = placar[0].text
        placar_home = int(placar.split('-')[0])
        placar_away = int(placar.split('-')[1])
        placar = f'{placar_home} X {placar_away}'
        # logging.warning(placar)
    else:
        placar_home = 0
        placar_away = 0
        placar = f'{placar_home} X {placar_away}'
        logging.warning('placar não encontrado, setou-se 0 a 0')

    # placares se não concluido
    placar_fav_jogando_em_casa_nao_concluido = ['0 X 1', '0 X 2', '1 X 2', '1 X 1']
    placar_fav_jogando_fora_nao_concluido = ['1 X 0', '2 X 0', '2 X 1', '1 X 1']

    # se 0 a 0 deleta a entrada do database de monitoramento
    if placar == '0 X 0':
        logging.warning('Jogo 0 a 0 (não deveria estar sendo monitorado)')
        delete_database(getenv('TABLE_ENTRADAS_EM_ANDAMENTO'), url)

    # se entrada não concluida...
    if favorito == 0 and placar in placar_fav_jogando_em_casa_nao_concluido:
        logging.warning(f'FAV jogando EM CASA e entrada não concluida, placar: {placar}')
    if favorito == 1 and placar in placar_fav_jogando_fora_nao_concluido:
        logging.warning(f'FAV jogando FORA e entrada não concluida, placar: {placar}')
        
    # se entrada concluída...
    if favorito == 0 and placar not in placar_fav_jogando_em_casa_nao_concluido:
        logging.warning(f'FAV jogando EM CASA e ENTRADA CONCLUÍDA, placar: {placar}')
        return True
    if favorito == 1 and placar not in placar_fav_jogando_fora_nao_concluido:
        logging.warning(f'FAV jogando FORA e ENTRADA CONCLUÍDA, placar: {placar}')
        return True
    
    return False

def pl_aproximado(odd_entrada, odd_saida):
    """
        Cálculo aproximado do Profit Loss
            params
            odd_entrada (float)
            odd_saida (float)
    """
    if odd_saida == 0.0:
        return 'Calculo indiponível, mercado aflito.'
    responsabilidade = 100
    stake = responsabilidade / (odd_entrada - 1)
    stake_fechamento = odd_entrada / odd_saida * stake
    pl = stake - stake_fechamento
    pl_formatado = f'{pl:.02f}%'

    return pl_formatado

def monitoramento_de_entradas(driver, entradas_em_andamento):
    """
        Recebe o driver e monitora as entradas do database de monitoramento e envia para o database de finalizadas.
    """
    logging.warning('iniciando monitoramento...')

    for entrada in entradas_em_andamento:
        try: 
            jogo = entrada[1]
            odd_entrada = entrada[3]
            favorito = entrada[4]
            id_sinal = entrada[5]
            url = entrada[6]
            competicao = entrada[7]
            profit_loss_ht = entrada[8]
            placar_ht = entrada[9]

            logging.warning(f'pl ht: {profit_loss_ht}')

            logging.warning(jogo)
            driver.get(url)

            driver.implicitly_wait(10)

            # deleta jogo do banco se url nao encontrado
            pagina_indisponivel = driver.find_elements('xpath', '//h2[@class="title"]')
            if bool(pagina_indisponivel):
                delete_database(getenv("TABLE_ENTRADAS_EM_ANDAMENTO"), url)
                logging.warning(f'Página indispónivel p o jogo: {jogo}')
                continue
                
            WebDriverWait(driver, 20, 3).until(lambda x: x.find_element('xpath', '//*[@class="star-favourites"]'))

            placar = driver.find_elements('xpath', '//span[@class="score"]')
            if bool(placar) and placar[0].text != '':
                placar = placar[0].text
            else:
                placar = 'Indefinido'

            # # Calculando Profit Loss
            if favorito == 0:
                odd_saida, lay, gap = gap_and_odd(driver, 6)
                fav_db = 'HOME'
            if favorito == 1:
                odd_saida, lay, gap = gap_and_odd(driver, 9)
                fav_db = 'AWAY'
            profit_loss = pl_aproximado(odd_entrada, odd_saida)
            logging.warning(f'Profit Loss: {profit_loss}')

            tempo = driver.find_elements('xpath', '//p[@class="time-elapsed inplay"]')
            tempo = tempo[0].text
            if tempo == 'Intervalo':
                tempo = 45
                if profit_loss_ht == 'NA':
                    logging.warning('atualizando profit_loss HT')
                    comando = f'UPDATE {getenv("TABLE_ENTRADAS_EM_ANDAMENTO")} SET `profit_loss_ht` = "{profit_loss}", `placar_ht` = "{placar}" WHERE (`url` = "{url}");'
                    database(comando)
            else:
                tempo = int(tempo.split("'")[0])
            logging.warning(f'tempo de jogo: {tempo}')

            # se green
            if entrada_concluido(driver, favorito):
                # notificar no telegram
                odd_saida = 1000
                profit_loss = pl_aproximado(odd_entrada, odd_saida)
#                 msg = f""" Entrada Concluída!!
# Green!!
# ~ {profit_loss}✅ ✅"""
#                 app.run(resultado_da_entrada(getenv('TELEGRAM_CHAT_ID'), id_sinal, msg))
                
                if tempo < 45:
                    profit_loss_ht =profit_loss
                    placar_ht = placar
                
                # salvar no profit_loss_ht
                comando = f'INSERT INTO {getenv("TABLE_ENTRADAS_ENCERRADAS")} (`data`, `jogo`, `profit_loss`, `favorito`, `odd_entrada`, `odd_saida`, `competicao`, `profit_loss_ht`, `placar_ht`) VALUES ("{datetime.today()}", "{jogo}", "{profit_loss}", "{fav_db}", "{odd_entrada}", "{odd_saida}", "{competicao}", "{profit_loss_ht}", "{placar_ht}")'
                database(comando)

                # DELETAR do database de monitoramento e colocar no database de entradas finalizadas
                delete_database(getenv("TABLE_ENTRADAS_EM_ANDAMENTO"), url)
                continue
            
            # se 70 min fecha (green ou red)
            if tempo > 69:
                """
                 Esse IF pode ser um problema e não mandar a msg de fechamento.
                """
                #if gap > 0 and gap < 6: 
                    # print(f'Fecho ok para o {jogo} - Mercado não está aflito')
                # else:
                #     print(f'Fechou com mercado aflito ({jogo})')
                
                # notificar no telegram
#                 msg = f"""⏰ ATENÇÃO!!!!⏰
# Feche a posição o mais rápido possível.
# PL(aproximado) = {profit_loss}
# """
#                 app.run(resultado_da_entrada(getenv('TELEGRAM_CHAT_ID'), id_sinal, msg))

                # salvar no profit_loss_ht
                comando = f'INSERT INTO {getenv("TABLE_ENTRADAS_ENCERRADAS")} (`data`, `jogo`, `profit_loss`, `favorito`, `odd_entrada`, `odd_saida`, `competicao`, `profit_loss_ht`, `placar_ht`) VALUES ("{datetime.today()}", "{jogo}", "{profit_loss}", "{fav_db}", "{odd_entrada}", "{odd_saida}", "{competicao}", "{profit_loss_ht}", "{placar_ht}")'
                database(comando)

                # DELETAR do database de monitoramento e colocar no database de entradas finalizadas
                delete_database(getenv("TABLE_ENTRADAS_EM_ANDAMENTO"), url)
                logging.warning('hora de fechar a posição')
        except:
            logging.error(f'Monitoramento fail. Verificação manual na entrada: {entrada}')
    logging.warning('monitoramento finalizado.')