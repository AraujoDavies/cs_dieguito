from selenium import webdriver
from time import sleep
from dotenv import load_dotenv
from defs_analise_jogos_dia import analise_jogos_do_dia
from os import getenv
from database import database
from defs_monitoramento_entradas import monitoramento_de_entradas
import logging, datetime, schedule
from betfair import Betfair
from helpers import jogos_selecionados, data_inicio
from resultado_do_dia import Traderbet
from telegram import enviar_no_telegram

logging.basicConfig(level=logging.WARNING, filename=f"logs/cs{datetime.datetime.now().strftime('%d-%m')}.log", encoding='utf-8', format="%(asctime)s - %(levelname)s: %(message)s")

load_dotenv()


def atualiza_database():
    jogos_para_analisar = betfair.lista_de_jogos()
    jogos_selecionados(jogos_para_analisar)

def resultado_do_dia(driver: webdriver):
    a = Traderbet(driver)
    a.login_traderbet()
    df = a.resultado_diario(100)
    if len(df) > 0:
        df = df[['Jogo', 'Percentual']]
        df.loc[len(df)] = ['Resultado do dia: ', df['Percentual'].sum()]
        resultado_do_dia = round(df['Percentual'][len(df) - 1], 2)
        df['Percentual'] = df['Percentual'].map(lambda x: f"{round(x,2)}%")
        msg = df.to_string(index=False)
        msg = " ".join(msg.split()).replace('> <','><')
        msg = msg.replace("%", "%\n").replace("Jogo Percentual", " 🚨📚Resumo de Hoje📚🚨 \n\n").replace("Resultado do dia", "\n 📈 Resultado")
        enviar_no_telegram(getenv('TELEGRAM_CHAT_ID'), msg)

# selenium grid
driver = webdriver.Remote(
    command_executor="http://localhost:4444",
    options=webdriver.ChromeOptions())

schedule.every().day.at("22:50").do(resultado_do_dia, driver=driver)
schedule.every().day.at("02:00").do(atualiza_database)

betfair = Betfair(driver)

print('Acessando betfair...')
betfair.acessar_page_e_aceitar_cookies()

print('ajustando visualização...')
betfair.exibindo_jogos_por_data()

print('armazenando jogos do dia no database...')
atualiza_database()

print('Atualizando data de inicio dos jogos.')
data_inicio(driver)

# coletando dados do banco de dados para iniciar o while
comando = f"SELECT * FROM {getenv('TABLE_ENTRADAS_EM_ANDAMENTO')}"
entradas_em_andamento = database(comando)

print('CS bot start')
if __name__ == '__main__':
    while True:
        # att variável jogos do dia
        comando = f'SELECT * FROM {getenv("TABLE_JOGOS_DO_DIA")};'
        jogos_do_dia = database(comando)
        volume_de_jogos = 0

        # analisando jogos
        volume_de_jogos = analise_jogos_do_dia(driver, jogos_do_dia) # return 0 (nenhum) 5(poucos) 10(muitos)
        driver.refresh()

        # monitoramento das entradas feitas
        comando = f"SELECT * FROM {getenv('TABLE_ENTRADAS_EM_ANDAMENTO')}"
        entradas_em_andamento = database(comando)
        monitoramento_de_entradas(driver, entradas_em_andamento)

        # jogos restantes:
        logging.warning(f"Jogos no banco de dados: {len(jogos_do_dia)}")

        # a cada 1 minuto faz uma nova análise
        if volume_de_jogos < 5:
            logging.warning("baixo volume de jogos")
            sleep(60)

        schedule.run_pending()