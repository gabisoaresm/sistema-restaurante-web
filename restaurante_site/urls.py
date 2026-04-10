"""
URL configuration for restaurante_site project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

from cardapio.views import RegistroView, LogoutConfirmView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('login/', LoginView.as_view(template_name='cardapio/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout-confirma/', LogoutConfirmView.as_view(), name='logout-confirma'),
    path('registro/', RegistroView.as_view(), name='registro'),

    # App cardapio
    path('', include('cardapio.urls')),
]
