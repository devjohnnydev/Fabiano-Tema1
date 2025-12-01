# Em core/urls.py
from django.urls import path
from . import views

# Em core/urls.py
urlpatterns = [
    path('', views.home_view, name='home'), # O porteiro
    path('planos/', views.planos_view, name='planos'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/clients/', views.admin_clients_view, name='admin_clients'),
    # Em core/urls.py
    path('teste-email-forca/', views.debug_email_view),
]