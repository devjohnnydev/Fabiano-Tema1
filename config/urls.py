# Em config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings # <--- Importante
from django.conf.urls.static import static # <--- Importante
from core import views as core_views
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', core_views.custom_logout_view, name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('subscriptions/', include('subscriptions.urls')),
    
    path('', include('analytics.urls')),
    path('', include('accounts.urls')),
    path('', include('core.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# --- ADICIONE ISTO NO FINAL ---
# Serve arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
