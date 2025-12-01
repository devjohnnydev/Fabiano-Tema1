from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from subscriptions.models import Subscription, Payment, Plan
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings


# Isso checa se o usuário é um 'superuser'. Se não, ele dá erro.
def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """
    Dashboard com Comparativo Mensal
    """
    # 1. KPIs Básicos
    total_users = get_user_model().objects.count()
    total_clients = Subscription.objects.filter(status='active').count()
    
    # Receita Total (Soma de tudo desde o início)
    total_revenue_data = Payment.objects.aggregate(total=Sum('amount'))
    total_revenue = total_revenue_data['total'] or 0

    # 2. Dados Mensais para o Gráfico e Comparação
    # Agrupa pagamentos por mês
    monthly_revenue = Payment.objects.annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Transforma em lista para podermos manipular índices ([-1], [-2])
    revenue_list = list(monthly_revenue)

    # 3. Cálculo da Comparação (Mês Atual vs Mês Passado)
    growth_percent = 0
    is_positive = True
    current_month_total = 0

    if len(revenue_list) >= 1:
        current_month_total = revenue_list[-1]['total'] # O último mês
    
    if len(revenue_list) >= 2:
        last_month_total = revenue_list[-1]['total']     # Mês Atual (ou último com venda)
        previous_month_total = revenue_list[-2]['total'] # Penúltimo mês
        
        if previous_month_total > 0:
            # Fórmula: ((Atual - Anterior) / Anterior) * 100
            growth_percent = ((last_month_total - previous_month_total) / previous_month_total) * 100
        else:
            growth_percent = 100 # Se antes era 0 e agora tem venda, cresceu 100%
            
        is_positive = growth_percent >= 0

    # 4. Prepara dados para o Chart.js
    chart_labels = [item['month'].strftime('%b/%Y') for item in revenue_list]
    # Converte Decimal para Float para o JS entender
    chart_data = [float(item['total']) for item in revenue_list]

    context = {
        'total_users': total_users,
        'total_clients': total_clients,
        'total_revenue': total_revenue,
        
        # Dados novos de crescimento
        'growth_percent': round(growth_percent, 1),
        'is_positive': is_positive,
        'current_month_total': current_month_total,
        
        # Dados do gráfico
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_clients_view(request):
    """
    Lista de todos os usuários e seus planos
    """
    # Busca usuários com seus dados de assinatura (select_related otimiza a busca)
    users = get_user_model().objects.select_related('subscription__plan').all().order_by('-date_joined')
    
    context = {
        'users': users
    }
    return render(request, 'core/admin_clients.html', context)

def home_view(request):
    """
    Landing Page Pública.
    """
    #if request.user.is_authenticated:
     #   return redirect('dashboard_home')
    
    # --- AQUI TÁ O SEGREDO ---
    # Buscamos os planos para mostrar na capa
    plans = Plan.objects.all().order_by('price_monthly')
    
    context = {
        'plans': plans
    }
    
    return render(request, 'core/landing.html', context)


def planos_view(request):
    """
    Mostra a página de preços (baseado no seu design).
    """

    # [LINHA NOVA] Busca os planos REAIS do banco de dados
    plans = Plan.objects.all().order_by('price_monthly') # Ordena do mais barato ao mais caro

    context = {
        'plans': plans  # [LINHA NOVA] Manda os planos para o HTML
    }
    return render(request, 'core/planos.html', context)


def custom_logout_view(request):
    """
    Faz o logout do usuário (forçado via GET)
    e o redireciona para a página de login ('home').
    """
    logout(request)
    return redirect('home')

def debug_email_view(request):
    try:
        send_mail(
            subject='Teste Forçado pelo Site',
            message='Se chegou, o settings.py está 100%.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER], # Manda pra você mesmo
            fail_silently=False, # <--- OBRIGA A DAR ERRO SE FALHAR
        )
        return HttpResponse("<h1>SUCESSO! Email enviado.</h1>")
    except Exception as e:
        return HttpResponse(f"<h1>ERRO:</h1> <p>{e}</p>")