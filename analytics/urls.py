# Em analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard_home'),
    # A rota 'settings' foi removida.
]