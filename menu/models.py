from django.db import models
from django.contrib.auth.models import User  # Importando o modelo de usuário padrão do Django

class DicionarioUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relacionando com o usuário
    user_dict = models.JSONField(default=dict)  # Usando JSONField para armazenar listas ou dicionários

    def __str__(self):
        return f"Dicionário do usuário: {self.usuario.username}"
