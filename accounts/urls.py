# Em accounts/urls.py (O CÓDIGO CORRETO E LIMPO)

from django.urls import path
from . import views  # <-- Importa o arquivo 'views.py' INTEIRO

urlpatterns = [
    # Aponta para a CLASSE 'AuthView' (com 'A' e 'V' maiúsculo)
    # e usa o '.as_view()'
    path('login/', views.AuthView.as_view(), name='login'),
]