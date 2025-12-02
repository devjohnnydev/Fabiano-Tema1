import logging
import requests
from django.core.files.base import ContentFile
from analytics.models import Profile
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Usar print em vez de logger para ver no log do Railway mais fácil
def save_youtube_channel_data(backend, user, response, *args, **kwargs):
    print(f"--- 🕵️‍♂️ PIPELINE INICIADO PARA: {user.email} ---")

    # Garante que é login do Google
    if backend.name != 'google-oauth2':
        print("Ignorando: Não é login Google.")
        return

    # Tenta pegar ou criar o perfil
    try:
        profile, created = Profile.objects.get_or_create(user=user)
    except Exception as e:
        print(f"Erro ao criar Profile: {e}")
        return

    access_token = response.get('access_token')
    if not access_token:
        print("Erro: Sem Access Token.")
        return

    try:
        print("Conectando API YouTube...")
        credentials = Credentials(token=access_token)
        youtube_service = build('youtube', 'v3', credentials=credentials)
        
        request = youtube_service.channels().list(
            part="id,snippet", 
            mine=True
        )
        api_response = request.execute()

        if api_response.get('items'):
            item = api_response['items'][0]
            
            # 1. SALVAR ID
            channel_id = item['id']
            profile.youtube_channel_id = channel_id
            profile.save()
            print(f"✅ ID do canal salvo: {channel_id}")

            # 2. SALVAR FOTO (FORÇANDO ATUALIZAÇÃO)
            # Removemos o 'if not user.profile_picture' para sempre atualizar
            thumbnails = item['snippet']['thumbnails']
            picture_url = thumbnails.get('high', thumbnails.get('medium', thumbnails.get('default')))['url']
            
            if picture_url:
                print(f"Baixando foto de: {picture_url}")
                image_response = requests.get(picture_url)
                
                if image_response.status_code == 200:
                    # Salva sobrescrevendo a anterior
                    user.profile_picture.save(
                        f"avatar_{user.id}.jpg", 
                        ContentFile(image_response.content), 
                        save=True
                    )
                    print("✅ Foto atualizada com sucesso!")
                else:
                    print(f"Erro ao baixar imagem: Status {image_response.status_code}")
        else:
            print("⚠️ Nenhum canal do YouTube encontrado para este usuário.")

    except Exception as e:
        print(f"🚨 ERRO CRÍTICO NO PIPELINE: {e}")