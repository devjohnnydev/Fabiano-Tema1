# Em config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', core_views.custom_logout_view, name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('subscriptions/', include('subscriptions.urls')),

    # [A ORDEM É IMPORTANTE]
    # O 'analytics' (dashboard)
    path('', include('analytics.urls')), # Tem '/dashboard/'

    # O 'accounts' (login) AGORA CONTROLA A "PORTA DA FRENTE"
    path('', include('accounts.urls')), # Tem '/' (com name='home')

    # O 'core' (planos, etc)
    path('', include('core.urls')), # Tem '/planos/'
]