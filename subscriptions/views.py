# Em subscriptions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription, Payment
from datetime import datetime, timedelta

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
        amount=plan.price_monthly # (Vamos simular o pagamento mensal)
    )

    # 6. Manda o usuário de volta para o Dashboard.
    # (No futuro, a gente adiciona uma mensagem de "Sucesso!")
    return redirect('dashboard_home')