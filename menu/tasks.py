from background_task import background
from .models import DicionarioUsuario
from .utils import buscar_cotacao_instantaneafunc
from django.contrib.auth.models import User


@background(schedule=0)  
def rodar_buscar_cotacao_instantaneafunc(usuario_id, ticker):
    print(f"iniciando monitoramento do usuário {usuario_id}, para o ativo {ticker}")
    buscar_cotacao_instantaneafunc(ticker=ticker, usuario_id=usuario_id)


def setar_buscar_cotacao_instantaneafunc(usuario_id):
    try:
        user = User.objects.get(id=usuario_id)
        dicionario_usuario = DicionarioUsuario.objects.get(usuario=user)
        user_dict = dicionario_usuario.user_dict

        for ticker, valores in user_dict.items():
            intervalo = int(valores["Tempo"]) 
            rodar_buscar_cotacao_instantaneafunc(usuario_id=usuario_id, ticker=ticker, schedule=intervalo * 60)

    except DicionarioUsuario.DoesNotExist:
        print(f"Usuário com ID {usuario_id} não tem dicionário de preferências.")



