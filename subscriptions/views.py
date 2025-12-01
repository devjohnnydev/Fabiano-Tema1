# Em subscriptions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription, Payment

# Em subscriptions/views.py

@login_required
def planos_view(request):
    plans = Plan.objects.all().order_by('price_monthly')
    user = request.user
    
    # Verifica se é anual
    is_annual = False
    if hasattr(user, 'subscription') and user.subscription.plan:
        sub = user.subscription
        if sub.start_date and sub.current_period_end:
            total_days = (sub.current_period_end - sub.start_date).days
            # Se a duração for maior que 60 dias, consideramos Anual
            if total_days > 60:
                is_annual = True

    context = {
        'plans': plans,
        'is_annual': is_annual # <--- Mandamos essa flag pro HTML
    }
    return render(request, 'analytics/planos.html', context)

# Em subscriptions/views.py

@login_required
def upgrade_plan_view(request, plan_id):
    new_plan = get_object_or_404(Plan, id=plan_id)
    user = request.user
    
    # 1. Descobre qual o ciclo que o usuário QUER pegar (Vem da URL)
    target_period = request.GET.get('period', 'monthly')

    # Pega a assinatura atual
    current_subscription = getattr(user, 'subscription', None)

    # --- ZONA DE BLOQUEIO E SEGURANÇA ---
    if current_subscription and current_subscription.plan and current_subscription.status == 'active':
        current_plan = current_subscription.plan
        
        # Cálculos de Data
        if current_subscription.current_period_end and current_subscription.start_date:
            today = timezone.now()
            days_left = (current_subscription.current_period_end - today).days
            
            # Calcula a duração total do ciclo atual para saber se é ANUAL
            # (Se a diferença entre início e fim for maior que 60 dias, é Anual)
            total_duration = (current_subscription.current_period_end - current_subscription.start_date).days
            is_currently_annual = total_duration > 60 

            # REGRA 1: Bloqueio de Downgrade de Preço (Enterprise -> Pro)
            if new_plan.price_monthly < current_plan.price_monthly:
                if days_left > 7:
                    messages.error(request, 'Downgrade bloqueado. Aguarde até faltar 7 dias para o vencimento.')
                    return redirect('planos')

            # REGRA 2: Bloqueio de Ciclo (Anual -> Mensal) [NOVO!]
            # Se ele é Anual E quer ir pro Mensal E falta mais de uma semana
            if is_currently_annual and target_period == 'monthly':
                if days_left > 7:
                    messages.error(request, 'Você possui um plano Anual vigente. Aguarde o fim do ciclo para migrar para o Mensal.')
                    return redirect('planos')

    # ---------------------------------------

    # 2. Define valores baseados no ciclo escolhido
    if target_period == 'annual':
        days_to_add = 365
        amount = new_plan.price_annual
        cycle_name = "Anual"
    else:
        days_to_add = 30
        amount = new_plan.price_monthly
        cycle_name = "Mensal"

    # 3. Processa a Assinatura
    subscription, created = Subscription.objects.get_or_create(user=user)
    subscription.plan = new_plan
    subscription.status = 'active'
    
    # Define datas
    subscription.start_date = timezone.now()
    subscription.current_period_end = timezone.now() + timedelta(days=days_to_add)
    subscription.save()

    # 4. Gera Pagamento
    if amount > 0:
        Payment.objects.create(
            user=user,
            subscription=subscription,
            amount=amount
        )

    messages.success(request, f'Sucesso! Plano {new_plan.name} ({cycle_name}) assinado até {subscription.current_period_end.strftime("%d/%m/%Y")}.')
    return redirect('settings')
# Tranca a view: se o usuário não estiver logado,
# ele é enviado para a página 'home' (nosso login).
@login_required(login_url='home')
def subscribe_view(request, plan_id):
    """
    Simula a "compra" de um plano.
    """
    # 1. Pega o plano que o usuário clicou (ou dá erro 404)
    plan = get_object_or_404(Plan, id=plan_id)
    user = request.user

    # 2. Pega a assinatura do usuário (ou cria uma nova)
    # Isso é "de alto nível": impede que o usuário tenha 2 assinaturas
    subscription, created = Subscription.objects.get_or_create(
        user=user,
        defaults={'plan': plan, 'status': Subscription.StatusChoices.ACTIVE}
    )

    # 3. Se a assinatura já existia (não foi 'created'),
    # apenas atualiza o plano e o status dela.
    if not created:
        subscription.plan = plan
        subscription.status = Subscription.StatusChoices.ACTIVE

    # 4. Define a data de "expiração" (daqui a 30 dias)
    subscription.current_period_end = datetime.now() + timedelta(days=30)
    subscription.save()

    # 5. CRIE O PAGAMENTO (O "KA-CHING!" 💰)
    # Isso é o que o seu Dashboard de Admin vai ler!
    Payment.objects.create(
        user=user,
        subscription=subscription,
        amount=plan.price_monthly # Ou o valor do plano
    )
    
    return redirect('dashboard_home')