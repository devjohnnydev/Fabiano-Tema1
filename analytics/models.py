# Em analytics/models.py
from django.db import models
from django.conf import settings # Importa as configurações do Django

class Profile(models.Model):
    # Link "um-para-um" com o nosso CustomUser (definido em settings.AUTH_USER_MODEL)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # O campo que vai guardar o ID do canal (salvo pelo pipeline)
    youtube_channel_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        # Esta é a função "rótulo" correta.
        # Ela pede ao modelo CustomUser para se apresentar (provavelmente usando o email).
        return f"Perfil de {str(self.user)}"