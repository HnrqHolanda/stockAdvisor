import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.contrib.auth.models import User

def enviar_recomendacao(id_usuario, Linf, Lsup, cotacao, ticker):
    try:
        
        usuario = User.objects.get(id=id_usuario)
        
        if float(cotacao) > float(Lsup):
            assunto = f"Recomendação de venda: {ticker}"
            mensagem = f"A cotação do ativo {ticker} está acima de {Lsup}. Recomendamos a venda do ativo."
        elif float(cotacao) < float(Linf):
            assunto = f"Recomendação de compra: {ticker}"
            mensagem = f"A cotação do ativo {ticker} está abaixo de {Linf}. Recomendamos a compra do ativo."
        else:
            return

       
        send_mail(
            assunto,
            mensagem,
            'no-reply@seusite.com',  
            [usuario.email],  
            fail_silently=False,
        )
    except User.DoesNotExist:
        print(f"Usuário com ID {id_usuario} não encontrado.")




def buscar_cotacao_instantaneafunc(ticker, usuario_id, Linf, Lsup):
    print(f"Iniciando busca de cotação para {ticker}")

    # Configuração do WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f"https://finance.yahoo.com/quote/{ticker}.SA/"
    driver.get(url)

    time.sleep(4)

    try:
        cotacao_element = driver.find_element(By.XPATH, "/html/body/div[2]/main/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/div[1]/span")
        cotacao = cotacao_element.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Cotação obtida: {cotacao} às {timestamp}")
    except Exception as e:
        print(f"Erro ao buscar cotação para {ticker}: {e}")
        cotacao = None
        timestamp = None

    driver.quit()

    if cotacao and timestamp:

        enviar_recomendacao(id_usuario=usuario_id, Linf=Linf, Lsup=Lsup, cotacao=cotacao, ticker=ticker)

        url_post = "http://127.0.0.1:8000/menu/atualizar_dict_cotacao/"  

        data = {
            'ticker': ticker,
            'timestamp': timestamp,
            'cotacao': cotacao,
            'id': usuario_id, 
        }

        try:
            response = requests.post(url_post, data=data)

            if response.status_code == 200:
                print(f"Cotação para {ticker} atualizada com sucesso.")
            else:
                print(f"Erro ao atualizar cotação para {ticker}. Código {response.status_code}. Resposta: {response.text}")

        except requests.RequestException as e:
            print(f"Erro na requisição POST para {url_post}: {e}")
    else:
        print(f"Não foi possível obter cotação para {ticker}.")





