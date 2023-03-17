from time import sleep
import logging
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup


class Betfair():
    def __init__(self, driver):
        self.d = driver

    def acessar_page_e_aceitar_cookies(self):
        """
            1. Acessa a url 
            2. Aceita cookies ao acessar página
        """
        self.d.get('https://www.betfair.com/exchange/plus/pt/futebol-apostas-1/today')
        self.d.maximize_window()
        try:
            WebDriverWait(self.d, 10).until(lambda x: x.find_element('xpath', '//button[@id="onetrust-accept-btn-handler"]'))
            aceitar_cookies = self.d.find_element('xpath', '//button[@id="onetrust-accept-btn-handler"]')
            sleep(1)
            aceitar_cookies.click()
            sleep(2)
            logging.warning('acessar_page_e_aceitar_cookies: Cookies aceitos!')
            return True
        except:
            logging.warning('acessar_page_e_aceitar_cookies: Não foi solicitado o aceite de cookies')

    def exibindo_jogos_por_data(self):
        """
            ajustar visualização por data nos jogos de hj
            deve estar na página: https://www.betfair.com/exchange/plus/pt/futebol-apostas-1/today
        """
        try:
            visualizar_por = self.d.find_element('xpath', '//div[@class="group-by-filter"]//*[@class="selected-option"]')
            visualizar_por.click()
            sleep(2)
            visualizar_por_data = self.d.find_element('xpath', '//*[@class="options-list"]//*[@title = "Data"]')
            visualizar_por_data.click()
            sleep(2)
            logging.warning('exibindo_jogos_por_data: visualização por DATA')
            return True
        except:
            logging.warning('exibindo_jogos_por_data: Já está no modo de visualização por DATA')

    def lista_de_jogos(self):
        """
            Retorna uma lista de jogos: cada jogo é um dict
            
            vai analisar todos os jogos q estiverem na tela, sendo today, tommorow or future
        """
        dados_dos_jogos = [] # armazena um dict com as informações dos jogos
        while 1 > 0:
            htmls = self.d.find_elements('xpath', '//div[@class="card-content"]')
            for html in htmls:
                html = html.get_attribute('innerHTML')
                soup = BeautifulSoup(html, "html.parser")
                # adicionando os jogos na lista
                jogos = soup.find_all('tr', attrs={'ng-repeat-start': '(marketId, event) in vm.tableData.events'})
                for jogo in jogos:
                    dict = {}
                    # Equipes, separando mandante e visitante
                    equipes = jogo.find('ul', class_='runners')
                    dict['mandante'] = equipes.find_all('li')[0].attrs['title']
                    dict['visitante'] = equipes.find_all('li')[1].attrs['title']
                    # ODDS
                    odds = jogo.find('td', "coupon-runners") # area de odds
                    odds_b = odds.find_all('button') # 6 botões
                    dict['odd_back_mandante'] = (
                        0 if odds_b[0].find('label').text == ''
                        else odds_b[0].find('label').text
                    )
                    dict['odd_back_visitante'] = (
                        0 if odds_b[-2].find('label').text == ''
                        else odds_b[-2].find('label').text
                    )
                    # coletar url
                    dict['url'] = f"https://www.betfair.com/exchange/plus/{jogo.td.find('a', 'mod-link').get('href')}"
                    # competição 
                    dict['competicao'] = dict['url'].split('/')[-2]
                    # Liquidez
                    dict['liquidez'] = float(jogo.find('li', class_="matched-amount-value").text.replace(',', '').replace('R$', ""))
                    # salvando na lista
                    dados_dos_jogos.append(dict)

            # quando parar o looping:
            sleep(10)
            proxima_pagina = self.d.find_elements('xpath', '//a[contains(@class,"coupon-page-navigation__link--next")]')
            if bool(proxima_pagina):
                ultima_pagina = "is-disabled" in proxima_pagina[0].get_attribute("class") # True se está na última página de análise
                if ultima_pagina == True:
                    logging.warning('lista_de_jogos - BREAK: última página')
                    break
            if bool(proxima_pagina) == False:
                logging.warning('lista_de_jogos - BREAK: não existe botão para próxima página')
                break
            proxima_pagina[0].click()
            sleep(5)

        logging.warning(f'{len(dados_dos_jogos)} jogos')
        return dados_dos_jogos