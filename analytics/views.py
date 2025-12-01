# Em analytics/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from . import youtube_service
import json
import logging
from django.core.cache import cache
import re
from textblob import TextBlob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


# --- [FUNÇÃO HELPER] ---
# (Colando ela aqui para garantir que ela exista)
def calculate_percentage_change(current, previous):
    if previous == 0:
        if current > 0:
            return 100.0 # Se saiu de 0 para >0, é 100% de aumento
        else:
            return 0.0 # Se era 0 e é 0, mudou 0%
    
    change = ((current - previous) / previous) * 100
    return round(change, 2) # Arredonda para 2 casas decimais
# ------------------------------


# --- [A VIEW INTEIRA E CORRIGIDA] ---
@login_required
def dashboard_view(request):
    
    context = {
        'error_message': None,
        'kpi_cards': {}, # Agora é um dict vazio
        'comparison_card': {}, # Novo card
        'insights_chart_data': None,
        'video_table_data': None,
        'region_chart_data': None,
    }

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.youtube_channel_id:
        # (Lógica de erro do canal)
        logger.warning(f"Usuário {request.user.email} não tem youtube_channel_id no perfil.")
        context['error_message'] = (
            "Não foi possível encontrar um ID de canal do YouTube associado à sua conta Google. "
            "Por favor, faça logout e tente logar com uma conta Google que seja proprietária de um canal."
        )
        return render(request, 'analytics/index.html', context)
    
    
    # --- LÓGICA DE CACHE (Igual) ---
    cache_key = f"dashboard_data_{request.user.id}"
    dashboard_data = cache.get(cache_key)
    
    if not dashboard_data:
        logger.info(f"Cache miss para {cache_key}. Buscando dados frescos da API...")
        dashboard_data = youtube_service.get_dashboard_data(request.user)
        if not dashboard_data.get('error'):
            cache.set(cache_key, dashboard_data, timeout=10800) 
    else:
        logger.info(f"Cache hit para {cache_key}. Usando dados cacheados.")
        

    
    # --- [O 'TRY' QUE ESTAVA ABERTO] ---
    try:
        if dashboard_data.get('error'):
            context['error_message'] = dashboard_data['error']
            return render(request, 'analytics/index.html', context)

        # --- a) Processa os KPIs (Atual vs. Anterior) ---
        def get_kpi_totals(data_block):
            totals = {}
            if not data_block.get('rows'): 
                return {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0, 'subscribers_net': 0}

            headers = {h['name']: i for i, h in enumerate(data_block.get('columnHeaders', []))}
            row = data_block['rows'][0]
            
            totals['views'] = row[headers.get('views', 0)]
            totals['likes'] = row[headers.get('likes', 0)]
            totals['comments'] = row[headers.get('comments', 0)]
            totals['shares'] = row[headers.get('shares', 0)]
            gained = row[headers.get('subscribersGained', 0)]
            lost = row[headers.get('subscribersLost', 0)]
            totals['subscribers_net'] = gained - lost
            
            return totals

        current_totals = get_kpi_totals(dashboard_data.get('kpi_current_period', {}))
        previous_totals = get_kpi_totals(dashboard_data.get('kpi_previous_period', {}))

        context['kpi_cards'] = {
            'views': current_totals['views'],
            'views_change': calculate_percentage_change(current_totals['views'], previous_totals['views']),
            'likes': current_totals['likes'],
            'likes_change': calculate_percentage_change(current_totals['likes'], previous_totals['likes']),
            'subscribers': current_totals['subscribers_net'],
            'subscribers_change': calculate_percentage_change(current_totals['subscribers_net'], previous_totals['subscribers_net']),
        }
        
        # --- (Onde o seu erro aconteceu) ---
        context['comparison_card'] = {
            'views': current_totals['views'],           # <-- [LINHA NOVA]
            'views_prev': previous_totals['views'],       # <-- [LINHA NOVA]
            'views_change': context['kpi_cards']['views_change'], # <-- [LINHA NOVA]
            'likes': current_totals['likes'],
            'likes_prev': previous_totals['likes'], 
            'likes_change': context['kpi_cards']['likes_change'],
            'comments': current_totals['comments'],
            'comments_prev': previous_totals['comments'], 
            'comments_change': calculate_percentage_change(current_totals['comments'], previous_totals['comments']),
            'shares': current_totals['shares'],
            'shares_prev': previous_totals['shares'], 
            'shares_change': calculate_percentage_change(current_totals['shares'], previous_totals['shares']),
        }

        # --- b) Processa o Gráfico de Insights ---
        analytics_data = dashboard_data.get('analytics_timeseries', {})
        analytics_rows = analytics_data.get('rows', [])
        analytics_headers = analytics_data.get('columnHeaders', []) 
        
        if analytics_rows and analytics_headers:
            header_map = {h['name']: i for i, h in enumerate(analytics_headers)}
            idx_day = header_map.get('day')
            idx_views = header_map.get('views')
            idx_likes = header_map.get('likes')

            def safe_int(value):
                try:
                    return int(value)
                except(TypeError, ValueError):
                    return 0

            if all([idx_day is not None, idx_views is not None, idx_likes is not None]):
                chart_labels = [row[idx_day] for row in analytics_rows]
                chart_views = [safe_int(row[idx_views]) for row in analytics_rows]
                chart_likes = [safe_int(row[idx_likes]) for row in analytics_rows]
                
                insights_data = {
                    'labels': chart_labels,
                    'datasets': [
                        { 'label': 'Visualizações', 'data': chart_views, 'backgroundColor': '#9D4EDD' },
                        { 'label': 'Likes', 'data': chart_likes, 'backgroundColor': '#E845A0' },
                    ]
                }
                context['insights_chart_data'] = json.dumps(insights_data)
        
        # --- c) Processa o Gráfico de Região ---
        region_rows = dashboard_data.get('region_data', {}).get('rows', [])
        if region_rows:
            region_labels = [row[0] for row in region_rows] 
            region_views = [row[1] for row in region_rows]
            region_data = {
                'labels': region_labels,
                'datasets': [{
                    'label': 'Visualizações por Região',
                    'data': region_views,
                    'backgroundColor': ['#9D4EDD', '#E845A0', '#00C49F', '#FFBB28', '#FF8042'],
                    'hoverOffset': 4
                }]
            }
            context['region_chart_data'] = json.dumps(region_data)

        # --- d) Processa a Tabela de Vídeos ---
        video_stats_list = dashboard_data.get('video_list_stats', [])
        table_rows = []
        for video in video_stats_list:
            table_rows.append({
                'title': video['snippet']['title'],
                'thumbnail': video['snippet']['thumbnails']['default']['url'],
                'status': 'Ativo',
                'likes': int(video['statistics'].get('likeCount', 0)),
                'comments': int(video['statistics'].get('commentCount', 0)),
            })
        context['video_table_data'] = table_rows
            
    # --- [O BLOCO QUE FALTAVA!] ---
    except Exception as e:
        logger.exception(f"Erro fatal ao processar dados na dashboard_view: {e}")
        context['error_message'] = f"Um erro inesperado ao processar dados: {e}"

    return render(request, 'analytics/index.html', context)
@login_required
def sentiment_analysis_view(request):
    context = {}
    user_videos = [] 
    
    # --- PASSO 1: BUSCAR VÍDEOS DO CANAL (Para o select) ---
    try:
        social = request.user.social_auth.get(provider='google-oauth2')
        credentials = Credentials(token=social.extra_data['access_token'])
        youtube = build('youtube', 'v3', credentials=credentials)

        request_videos = youtube.search().list(
            part="snippet", forMine=True, type="video", maxResults=10, order="date"
        )
        response_videos = request_videos.execute()

        for item in response_videos['items']:
            user_videos.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title']
            })
    except Exception as e:
        context['error'] = "Não foi possível carregar seus vídeos. Verifique o login Google."

    # --- PASSO 2: PROCESSAR ANÁLISE (Quando clica no botão) ---
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        
        print(f"\n--- 🕵️‍♂️ DEBUG INICIADO ---")
        print(f"1. ID Recebido: {video_id}")

        if video_id:
            try:
                # 2.1 Busca o Título do Vídeo específico (Pra ficar bonito na tela)
                video_response = youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                
                video_title = "Vídeo sem título"
                if video_response['items']:
                    video_title = video_response['items'][0]['snippet']['title']
                
                print(f"2. Título encontrado: {video_title}")

                # 2.2 Busca os Comentários
                response_comments = youtube.commentThreads().list(
                    part="snippet", videoId=video_id, maxResults=50, textFormat="plainText"
                ).execute()
                
                comments_data = []
                positive = 0
                negative = 0
                neutral = 0
                
                translator = GoogleTranslator(source='auto', target='en')

                print(f"3. Iniciando análise de {len(response_comments['items'])} comentários...")

                for item in response_comments['items']:
                    raw_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    
                    # Tradução
                    try:
                        translated_text = translator.translate(raw_text)
                    except:
                        translated_text = raw_text

                    # Análise
                    blob = TextBlob(translated_text)
                    polarity = blob.sentiment.polarity
                    
                    if polarity > 0.1:
                        sentiment = 'Positivo'
                        positive += 1
                    elif polarity < -0.1:
                        sentiment = 'Negativo'
                        negative += 1
                    else:
                        sentiment = 'Neutro'
                        neutral += 1
                        
                    comments_data.append({
                        'author': author,
                        'original': raw_text,    # O HTML usa .original
                        'translated': translated_text, # O HTML usa .translated
                        'sentiment': polarity    # O HTML usa o número para decidir a cor
                    })
                
                # --- AQUI ESTAVA O ERRO DE COMPATIBILIDADE ---
                # O Template espera 'summary' com chaves 'positive', 'neutral', 'negative'
                summary_data = {
                    'positive': positive,
                    'negative': negative,
                    'neutral': neutral,
                    'total': positive + negative + neutral
                }

                print(f"4. SUCESSO! Resumo: {summary_data}")

                # Atualiza o contexto com os nomes CERTOS pro HTML
                context.update({
                    'summary': summary_data,      # <--- Agora bate com {% if summary %}
                    'comments': comments_data,    # <--- Agora bate com {% for comment in comments %}
                    'video_title': video_title,
                    'selected_video_id': video_id
                })
                
            except Exception as e:
                print(f"🚨 ERRO CRÍTICO NA ANÁLISE: {e}")
                context['error'] = f"Erro ao analisar: {str(e)}"

    context['user_videos'] = user_videos
    return render(request, 'analytics/sentiment.html', context)