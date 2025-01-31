from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from menu.tasks import setar_buscar_cotacao_instantaneafunc  

@receiver(user_logged_in)
def iniciar_tarefas_no_login(sender, request, user, **kwargs):
    print(f"Usuário {user.username} logado. Iniciando tarefas.")
    setar_buscar_cotacao_instantaneafunc(usuario_id=user.id)
