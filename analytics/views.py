# Em analytics/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from . import youtube_service
import json
import logging
from django.core.cache import cache # <-- [NOVO] IMPORTA O CACHE

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    
    context = {
        'error_message': None,
        'kpi_cards': None,
        'insights_chart_data': None,
        'video_table_data': None,
        'region_chart_data': None, # <-- [NOVO] Para o gráfico de Região
    }

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile, created = Profile.objects.get_or_create(user=request.user)

    if not profile.youtube_channel_id:
        logger.warning(f"Usuário {request.user.email} não tem youtube_channel_id no perfil.")
        context['error_message'] = (
            "Não foi possível encontrar um ID de canal do YouTube associado à sua conta Google. "
            "Por favor, faça logout e tente logar com uma conta Google que seja proprietária de um canal."
        )
        return render(request, 'analytics/index.html', context)
    
    
    # --- [MUDANÇA CRUCIAL: LÓGICA DE CACHE] ---
    
    # 1. Define uma chave de cache única para este usuário
    cache_key = f"dashboard_data_{request.user.id}"
    
    # 2. Tenta pegar os dados do cache PRIMEIRO
    dashboard_data = cache.get(cache_key)
    
    if not dashboard_data:
        # 3. Se NÃO ESTÁ NO CACHE (ou expirou):
        logger.info(f"Cache miss para {cache_key}. Buscando dados frescos da API...")
        
        # Chama nosso serviço 'caro'
        dashboard_data = youtube_service.get_dashboard_data(request.user)
        
        # 4. Salva os dados no cache por 3 horas (10800 segundos)
        #    (Não salve se houver um erro!)
        if not dashboard_data.get('error'):
            cache.set(cache_key, dashboard_data, timeout=10800) 
    else:
        # 5. Se ESTÁ NO CACHE:
        logger.info(f"Cache hit para {cache_key}. Usando dados cacheados.")
        
    # --- [FIM DA LÓGICA DE CACHE] ---
        

    # Agora, o resto da view processa 'dashboard_data' (seja do cache ou da API)
    try:
        if dashboard_data.get('error'):
            context['error_message'] = dashboard_data['error']
            return render(request, 'analytics/index.html', context)

        # --- a) Processa os KPIs (Igual) ---
        analytics_rows = dashboard_data.get('analytics_timeseries', {}).get('rows', [])
        if analytics_rows:
            total_views = sum(row[1] for row in analytics_rows)
            total_likes = sum(row[2] for row in analytics_rows)
            context['kpi_cards'] = {
                'views': total_views,
                'likes': total_likes,
            }
        
        # --- b) Processa o Gráfico de Insights (Igual) ---
        if analytics_rows:
            chart_labels = [row[0] for row in analytics_rows]
            chart_views = [row[1] for row in analytics_rows]
            chart_likes = [row[2] for row in analytics_rows]
            insights_data = {
                'labels': chart_labels,
                'datasets': [
                    { 'label': 'Visualizações', 'data': chart_views, 'backgroundColor': '#9D4EDD' },
                    { 'label': 'Likes', 'data': chart_likes, 'backgroundColor': '#E845A0' },
                ]
            }
            context['insights_chart_data'] = json.dumps(insights_data)

        # --- [NOVO] c) Processa o Gráfico de Região ---
        region_rows = dashboard_data.get('region_data', {}).get('rows', [])
        if region_rows:
            # region_rows = [['BR', 5000], ['US', 3000], ...]
            region_labels = [row[0] for row in region_rows] # Países (ex: 'BR', 'US')
            region_views = [row[1] for row in region_rows]  # Views
            
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

        # --- [ATUALIZADO] d) Processa a Tabela de Vídeos ---
        video_stats_list = dashboard_data.get('video_list_stats', [])
        video_impressions = dashboard_data.get('video_impressions', {}) # Pega o novo dict
        table_rows = []
        for video in video_stats_list:
            video_id = video['id'] # Pega o ID do vídeo
            table_rows.append({
                'title': video['snippet']['title'],
                'thumbnail': video['snippet']['thumbnails']['default']['url'],
                'status': 'Ativo',
                'likes': int(video['statistics'].get('likeCount', 0)),
                'impressions': video_impressions.get(video_id, 0), # <-- [MUDANÇA] Pega do dict
                'comments': int(video['statistics'].get('commentCount', 0)),
            })
        context['video_table_data'] = table_rows
            
    except Exception as e:
        logger.exception(f"Erro fatal ao processar dados na dashboard_view: {e}")
        context['error_message'] = f"Um erro inesperado ao processar dados: {e}"

    return render(request, 'analytics/index.html', context)

# ... (Não mexa no app 'accounts' ou em outros arquivos) ...