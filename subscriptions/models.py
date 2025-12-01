from django.db import models
from django.conf import settings


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_annual = models.DecimalField(max_digits=10, decimal_places=2)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Nome do ícone do Material Symbols (ex: 'auto_awesome')")

    def __str__(self) -> str:
        return str(self.name)


class Subscription(models.Model):
    
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        CANCELED = 'canceled', 'Cancelada'
        PAST_DUE = 'past_due', 'Vencida'
        FREE_TRIAL = 'free_trial', 'Trial Gratuito'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.FREE_TRIAL)
    
    start_date = models.DateTimeField(auto_now_add=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        user_email = getattr(self.user, 'email', 'Unknown') if self.user else 'No User'
        plan_name = self.plan.name if self.plan else 'Sem Plano'
        return f"{user_email} - {plan_name} ({self.status})"


class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        user_email = getattr(self.user, 'email', 'Usuário Deletado') if self.user else 'Usuário Deletado'
        return f"Pagamento de {self.amount} por {user_email}"
