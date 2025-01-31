from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.contrib.auth import login as login_django
from menu.views import iniciar_coleta_periodica
from threads import threads_ativas
from menu.models import DicionarioUsuario

def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")
    else:
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "As senhas não coincidem.")
            return redirect("/auth/cadastro")


        if User.objects.filter(username=username).exists():
            messages.error(request, "O nome de usuário já está em uso.")
            return redirect("/auth/cadastro")

        if User.objects.filter(email=email).exists():
            messages.error(request, "O e-mail já está cadastrado.")
            return redirect("/auth/cadastro")

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return redirect("/auth/login")


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login_django(request, user)
            
            try:
                dicionario_usuario = DicionarioUsuario.objects.get(usuario=user)
                user_dict = dicionario_usuario.user_dict
                for ticker, dados in user_dict.items():
                    Linf = dados.get("Linf")
                    Lsup = dados.get("Lsup")
                    Tempo = dados.get("Tempo")
                    
                    
                    iniciar_coleta_periodica(user.id, ticker, int(Tempo), Linf, Lsup)
            except DicionarioUsuario.DoesNotExist:
                print("Dicionário do usuário não encontrado.")
            
            return redirect("/menu/monitoramento")
        else:
            messages.error(request, "Usuário ou senha inválidos")
            return redirect("/auth/login")

