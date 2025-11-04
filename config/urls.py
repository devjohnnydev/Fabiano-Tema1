# Em config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # O Dashboard (app 'analytics') continua na raiz
    path('', include('analytics.urls')),
    
    # O Login (app 'accounts') agora vive em "accounts/"
    path('accounts/', include('accounts.urls')), # <-- CORRIGIDO
    path('social/', include('social_django.urls', namespace='social')),
]