# Em accounts/pipeline.py
import logging
from analytics.models import Profile
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

def save_youtube_channel_id(backend, user, response, *args, **kwargs):
    """
    Esta função é chamada DEPOIS que o usuário se autentica com o Google.
    Vamos usar o 'access_token' para buscar o ID do canal do usuário.
    """

    # 1. GARANTE A CRIAÇÃO DO PERFIL (A CORREÇÃO!)
    #    Esta linha executa PRIMEIRO. Ela cria o perfil se ele não existir.
    profile, created = Profile.objects.get_or_create(user=user)

    # 2. Agora podemos checar com segurança se o ID está faltando.
    if kwargs.get('is_new', False) or not profile.youtube_channel_id:
        access_token = response.get('access_token')

        if not access_token:
            logger.warning(f"Não foi possível encontrar o access_token para o usuário {user.email}")
            return

        try:
            # 3. Constrói as credenciais e o serviço
            credentials = Credentials(token=access_token)
            youtube_service = build('youtube', 'v3', credentials=credentials)

            # 4. Faz a chamada
            request = youtube_service.channels().list(
                part="id",
                mine=True
            )
            api_response = request.execute()

            # 5. Verifica e salva o ID
            if api_response.get('items'):
                channel_id = api_response['items'][0]['id']

                # 6. Nós JÁ TEMOS o perfil, apenas atualizamos e salvamos.
                profile.youtube_channel_id = channel_id
                profile.save()
                logger.info(f"ID do canal {channel_id} salvo para o usuário {user.email}")
            else:
                logger.warning(f"Usuário {user.email} logou, mas não possui um canal no YouTube.")

        except HttpError as e:
            logger.error(f"Erro na API do YouTube ao buscar ID do canal: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado no pipeline 'save_youtube_channel_id': {e}")