import logging
from os import getenv
from dotenv import load_dotenv
import pandas as pd
from time import sleep
import datetime

load_dotenv()

class Traderbet():
    def __init__(self, driver):
        self.driver = driver
        self.driver.get('https://www.tradexbr.com/customer/account/profitandloss/1')
        self.driver.maximize_window()
        self.user = getenv('USERNAME_TRADERBET')
        self.password = getenv('PASSWORD_TRADERBET')


    def login_traderbet(self):
        """faz login na traderbet caso nao esteja logado"""
        self.driver.implicitly_wait(10)
        input_user = self.driver.find_elements('xpath', '//input[@placeholder="Username"]')
        valida_url = 'tradexbr' in self.driver.current_url

        if bool(input_user) and valida_url: # se não está logado e está no site da traderbet, entao logue
            # preenchendo user
            self.driver.find_element('xpath', '//input[@placeholder="Username"]').send_keys(self.user)
            # preenchendo senha
            self.driver.find_element('xpath', '//input[@placeholder="Senha"]').send_keys(self.password)
            # submit
            self.driver.find_element('xpath', '//span[@class="js-login biab_login-submit"]').click()
            # aceitar termos
            self.driver.implicitly_wait(10)
            self.driver.find_element('xpath', '//div[@class="biab_btn-continue js-continue"]').click()
            logging.warning('logou!')
        else: 
            logging.warning('já está logado!')

    def resultado_diario(self, stake: int, dia: str):
        """
            Entra na pagina de PL e retorna as entradas em um DF

            ex: dia => 10-02-2023
        """
        sleep(5)
        # click ultimos 3 meses
        self.driver.find_element('xpath', '//*[@id="ui-id-2-button"]').click()
        self.driver.find_element('xpath', '//*[@id="ui-id-8"]').click()
        sleep(5)
        # click 100 jogos
        self.driver.find_element('xpath', '//*[@data-value="100"]').click()
        sleep(5)
        
        a = self.driver.find_element('xpath', '//div[@class="biab_table-holder"]').get_attribute('innerHTML')
        
        df = pd.read_html(a)
        df = df[0]
        df = df.rename(columns={'Mercado': 'game/market', 'Lucros e Perdas': 'PL_initial'})
        
        # Separando dia e hora
        df[['Data', 'hora']] = df['Data estabelecida'].str.split(' ', expand=True)

        # ajustando data
        df[['Dia', 'prep_mes', 'ano']] = df['Data'].str.split('-', expand=True)
        df['Mes'] = df['prep_mes']

        # Calculando PL real
        df['PL_final'] = round(df['PL_initial'].map( lambda x : x * 0.965 if x >= 0 else x), 2)

        # Separando game/market
        df[['Jogo', 'Mercado']] = df['game/market'].str.split('/ ', expand=True)

        # Responsabilidade + percent
        df['Responsabilidade'] = stake
        df['Percentual'] = round((df['PL_final'] / df['Responsabilidade']) * 100, 2)

        # Selecionando tabelas que quero
        df['id'] = df["Jogo"] + df['Data']
        df['id'] = df['id'].str.replace(' ', '')
        df = df[['id', 'Data', 'Data estabelecida', 'Mes', 'Jogo', 'Mercado', 'PL_initial', 'Responsabilidade', 'PL_final', 'Percentual']]

        # if mes != None:        
        #     seletor = (df['Mes'] == str(mes)) & (df['Mercado'] == 'Placar Exato')
        #     df = df[seletor]

        seletor =  df['Data'] == dia
        # retorna dia atual
        df = df[seletor]

        return df