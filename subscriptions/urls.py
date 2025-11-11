# Em subscriptions/urls.py (ARQUIVO NOVO)
from django.urls import path
from . import views

urlpatterns = [
    # A URL será: /subscriptions/subscribe/1/ (onde 1 é o ID do plano)
    path('subscribe/<int:plan_id>/', views.subscribe_view, name='subscribe'),
]