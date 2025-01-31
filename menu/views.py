from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import DicionarioUsuario
from .utils import buscar_cotacao_instantaneafunc
from django.http import JsonResponse
from django.contrib.auth.models import User
import threading
import csv
import json
import time
from django.views.decorators.csrf import csrf_exempt
from threads import threads_ativas


def iniciar_coleta_periodica(usuario_id, ticker, intervalo, Linf, Lsup):
    print("Iniciou coleta")

    flag_continuar = True

    def coleta():
        print("Tá coletando no intervalo")

        while flag_continuar:  
            buscar_cotacao_instantaneafunc(ticker, usuario_id, Linf=Linf, Lsup=Lsup)
            time.sleep(intervalo * 60)  

        print(f"Coleta para o ticker {ticker} interrompida.")

    
    def parar_coleta():
        nonlocal flag_continuar
        flag_continuar = False

    
    thread = threading.Thread(target=coleta, name=ticker, daemon=True)
    threads_ativas[ticker] = {'thread': thread, 'parar': parar_coleta}
    thread.start()


def interromper_coleta(ticker):
    if ticker in threads_ativas:
        threads_ativas[ticker]['parar']()  
        print(f"Interrompendo a coleta para o ticker {ticker}")

@login_required
def atualizar_dict_ativo(request):
    if request.method == 'POST':
        codigo = request.POST.get("codigo")
        Linf = request.POST.get('Linf')
        Lsup = request.POST.get('Lsup')
        Tempo = request.POST.get("Tempo")  
        acao = request.POST.get('acao')

        print(acao)

       
        dicionario_usuario = DicionarioUsuario.objects.get(usuario=request.user)
        user_dict = dicionario_usuario.user_dict

        if acao == 'adicionar':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                interromper_coleta(codigo)  

            user_dict[codigo] = {'Linf': Linf, 'Lsup': Lsup, 'Tempo': Tempo}  
            iniciar_coleta_periodica(request.user.id, codigo, int(Tempo))

        elif acao == 'remover':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                interromper_coleta(codigo) 

            user_dict.pop(codigo, None)

        elif acao == 'update':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                interromper_coleta(codigo)  

            user_dict[codigo]['Linf'] = Linf
            user_dict[codigo]['Lsup'] = Lsup
            user_dict[codigo]['Tempo'] = Tempo

            iniciar_coleta_periodica(request.user.id, codigo, int(Tempo), Linf=Linf, Lsup=Lsup)

   
        dicionario_usuario.user_dict = user_dict
        dicionario_usuario.save()

      
        return JsonResponse({'status': 'success', 'acao': acao, 'codigo': codigo})
    else:
        return JsonResponse({'status': 'error'}, status=400)



@login_required
def monitoramento(request):
    dicionario_usuario = DicionarioUsuario.objects.get(usuario=request.user)
    user_dict = dicionario_usuario.user_dict

    ativos = []


    for codigo, valores in user_dict.items():

        ativo_data = {
            "codigo": codigo,
            "Linf": valores["Linf"],
            "Lsup": valores["Lsup"],
        }

        if len(valores) > 3:
            timestamps = [key for key in valores.keys() if key not in ["Linf", "Lsup", "Tempo"]]
            
            timestamps.sort()

            ultimo_horario = timestamps[-1]
            ultima_cotacao = valores[ultimo_horario]

            data, hora = ultimo_horario.split(" ")

            if(float(ultima_cotacao) > float(valores["Lsup"])):
                ativo_data["Recomendação"] = "Vender"
            elif(float(ultima_cotacao) < float(valores["Linf"])):
                ativo_data["Recomendação"] = "Comprar"
            else:
                ativo_data["Recomendação"] = "Manter"

            ativo_data["ultimo_horario"] = hora
            ativo_data["ultima_cotacao"] = round(float(ultima_cotacao), 2) 
            ativo_data["ultima_data"] = data
        else:
            ativo_data["ultimo_horario"] = "---"
            ativo_data["ultima_data"] = "---"
            ativo_data["ultima_cotacao"] = "---"
            ativo_data["Recomendação"] = "---"

        ativos.append(ativo_data)


    return render(request, "monitoramento.html", {"ativos": ativos})

@login_required
def registros(request):
    dicionario_usuario = DicionarioUsuario.objects.get(usuario=request.user)
    user_dict = dicionario_usuario.user_dict

    

    registros_json = json.dumps(user_dict)
    print(registros_json)
    return render(request, "registros.html", {'registros_json': registros_json})

@login_required
def opções(request):

    dicionario_usuario = DicionarioUsuario.objects.get(usuario=request.user)
    user_dict = dicionario_usuario.user_dict

    caminho_csv = "menu/data/lista_ações.csv"  
    ativos = []
    with open(caminho_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticker = row["Ticker"]
            nome = row["Nome"]

            if ticker in user_dict:
                Linf = user_dict[ticker]["Linf"]
                Lsup = user_dict[ticker]["Lsup"]
                Tempo = user_dict[ticker]["Tempo"]
                checked = "checked"
            else:
                Linf = ""  
                Lsup = ""  
                checked = ""
                Tempo = ""

            ativos.append({
                "ticker": ticker,
                "nome": nome,
                "Linf": Linf,
                "Lsup": Lsup,
                "Tempo": Tempo,
                "checked": checked
            })
    

    return render(request, "opções.html", {"ativos": ativos})

@login_required
def atualizar_dict_ativo(request):
    if request.method == 'POST':
        codigo = request.POST.get("codigo")
        Linf = request.POST.get('Linf')
        Lsup = request.POST.get('Lsup')
        Tempo = request.POST.get("Tempo")  
        acao = request.POST.get('acao')

        print(acao)

        
        dicionario_usuario = DicionarioUsuario.objects.get(usuario=request.user)
        user_dict = dicionario_usuario.user_dict

        if acao == 'adicionar':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                del threads_ativas[codigo]

            user_dict[codigo] = {'Linf': Linf, 'Lsup': Lsup, 'Tempo': Tempo}  
            iniciar_coleta_periodica(request.user.id, codigo, int(Tempo), Linf=Linf, Lsup=Lsup)

        elif acao == 'remover':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                del threads_ativas[codigo]

            user_dict.pop(codigo, None)

        elif acao == 'update':
            if codigo in threads_ativas:
                print(f"Parando thread do ativo {codigo} antes de reiniciar.")
                del threads_ativas[codigo]

            user_dict[codigo]['Linf'] = Linf
            user_dict[codigo]['Lsup'] = Lsup
            user_dict[codigo]['Tempo'] = Tempo

            iniciar_coleta_periodica(request.user.id, codigo, int(Tempo), Linf=Linf, Lsup=Lsup)

        
        dicionario_usuario.user_dict = user_dict
        dicionario_usuario.save()

        
        return JsonResponse({'status': 'success', 'acao': acao, 'codigo': codigo})
    else:
        return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def atualizar_dict_cotacao(request):
    if request.method == 'POST':
        ticker = request.POST.get("ticker")
        timestamp = request.POST.get('timestamp')
        cotação = request.POST.get("cotacao")
        usuario_id = request.POST.get("id")


        user = User.objects.get(id=usuario_id)
        dicionario_usuario = DicionarioUsuario.objects.get(usuario=user)
        user_dict = dicionario_usuario.user_dict


        user_dict[f"{ticker}"][f"{timestamp}"] = cotação


        
        dicionario_usuario.user_dict = user_dict
        dicionario_usuario.save()

       
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'}, status=400)

def get_cotacao(request):
    ticker = request.GET.get('ticker')
    print(f"chegou aqui {ticker}")
    if ticker:
        timestamp, cotacao = buscar_cotacao_instantaneafunc(ticker)
        if timestamp and cotacao:
            return JsonResponse({
                'timestamp': timestamp,
                'cotacao': cotacao
            })
        else:
            return JsonResponse({'error': 'Erro ao buscar cotação'}, status=400)
    else:
        return JsonResponse({'error': 'Ticker não fornecido'}, status=400)


def customlogout(request):
   
    for codigo in list(threads_ativas.keys()):
        interromper_coleta(codigo)

    logout(request)
    return redirect('/auth/login')
