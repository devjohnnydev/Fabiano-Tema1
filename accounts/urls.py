from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Importe as views nativas

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('settings/', views.settings_view, name='settings'),

    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('disconnect-google/', views.disconnect_google_view, name='disconnect_google'), # <--- ESTA QUE FALTAVA

    # --- ROTAS DE ESQUECI MINHA SENHA ---
    # 1. Página para pedir o email
    # Em accounts/urls.py

    path('password_reset/', views.DebugPasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html'
    ), name='password_reset'),
    
    # 2. Página de "Email enviado"
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    
    # 3. Link que vem no email (Resetar senha)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    
    # 4. Sucesso!
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]