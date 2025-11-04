# Em accounts/urls.py
from django.urls import path
from .views import AuthView, logout_view 
# Removemos o dashboard_view, ele não pertence a este app

urlpatterns = [
    # Esta rota agora será: /accounts/login/
    path('login/', AuthView.as_view(), name='login'), 
    
    # Esta rota agora será: /accounts/logout/
    path('logout/', logout_view, name='logout'),
    
    # OBS: Se sua 'AuthView' também cuida do registro, tudo bem.
    # Se não, você adicionaria o 'register' aqui também:
    # path('register/', RegisterView.as_view(), name='register'),
]