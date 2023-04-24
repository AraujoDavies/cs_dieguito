from selenium import webdriver
from time import sleep
from dotenv import load_dotenv
from defs_analise_jogos_dia import analise_jogos_do_dia
from os import getenv
from database import database
import logging
from betfair import Betfair
from helpers import jogos_selecionados, data_inicio
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

# logging.basicConfig(level=logging.WARNING, filename=f"logs/cs{datetime.datetime.now().strftime('%d-%m')}.log", encoding='utf-8', format="%(asctime)s - %(levelname)s: %(message)s")
logging.basicConfig(encoding='utf-8', format="%(asctime)s - %(levelname)s: %(message)s")

load_dotenv()

def atualiza_database():
    jogos_para_analisar = betfair.lista_de_jogos()
    jogos_selecionados(jogos_para_analisar)

# selenium grid
# driver = webdriver.Remote(
#     command_executor="http://localhost:4444",
#     options=webdriver.ChromeOptions())

driver = webdriver.Chrome(service=service)

betfair = Betfair(driver)

logging.warning('Acessando betfair...')
betfair.acessar_page_e_aceitar_cookies()

logging.warning('ajustando visualização...')
betfair.exibindo_jogos_por_data()

logging.warning('armazenando jogos do dia no database...')
atualiza_database()

logging.warning('Atualizando data de inicio dos jogos.')
data_inicio(driver)

# coletando dados do banco de dados para iniciar o while
comando = f"SELECT * FROM {getenv('TABLE_ENTRADAS_EM_ANDAMENTO')}"
entradas_em_andamento = database(comando)

logging.warning('CS bot start')
if __name__ == '__main__':
    while True:
        # att variável jogos do dia
        comando = f'SELECT * FROM {getenv("TABLE_JOGOS_DO_DIA")};'
        jogos_do_dia = database(comando)
        volume_de_jogos = 0

        # analisando jogos
        volume_de_jogos = analise_jogos_do_dia(driver, jogos_do_dia) # return 0 (nenhum) 5(poucos) 10(muitos)
        driver.refresh()

        # # monitoramento das entradas feitas
        # comando = f"SELECT * FROM {getenv('TABLE_ENTRADAS_EM_ANDAMENTO')}"
        # entradas_em_andamento = database(comando)
        # monitoramento_de_entradas(driver, entradas_em_andamento)

        # jogos restantes:
        logging.warning(f"Jogos no banco de dados: {len(jogos_do_dia)}")

        # a cada 1 minuto faz uma nova análise
        if volume_de_jogos < 5:
            logging.warning("baixo volume de jogos")
            sleep(60)