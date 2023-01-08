from correct_score.betfair import Betfair
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

betfair = Betfair(driver)

def test_class_betfair_isworking():
    assert betfair.acessar_page_e_aceitar_cookies() == True
    assert betfair.exibindo_jogos_por_data() == True
    assert len(betfair.lista_de_jogos()) > 0

