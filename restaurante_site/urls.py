# =============================================================================
# urls.py — Rotas raiz do projeto restaurante_site.
#
# Responsável pelas rotas de autenticação (login, logout, registro)
# e pela inclusão das rotas do app cardapio.
# As rotas de autenticação ficam aqui (sem namespace) porque usam
# as views built-in do Django e precisam ser referenciadas como
# {% url 'login' %}, {% url 'logout' %} etc.
# =============================================================================

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

from cardapio.views import RegistroView, LogoutConfirmView

urlpatterns = [

    # Painel de administração do Django
    path('admin/', admin.site.urls),

    # ── Autenticação ──────────────────────────────────────────────────────────
    # LoginView usa o template do app cardapio em vez do template padrão do Django
    path('login/', LoginView.as_view(template_name='cardapio/login.html'), name='login'),
    # LogoutView (Django 5+) exige POST — o formulário fica em logout_confirma.html
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # Página intermediária que confirma o logout antes de fazer o POST
    path('logout-confirma/', LogoutConfirmView.as_view(), name='logout-confirma'),
    # Registro de novo usuário com escolha de tipo de perfil
    path('registro/', RegistroView.as_view(), name='registro'),

    # ── App cardapio ──────────────────────────────────────────────────────────
    # Inclui todas as rotas do app com o namespace 'cardapio'
    path('', include('cardapio.urls')),
]
