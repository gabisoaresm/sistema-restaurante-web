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
from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)

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

    # ── Recuperação de senha (usuário esqueceu a senha) ──────────────────────
    # Fluxo de 4 etapas do Django: formulário → enviado → confirmar → completo
    # ATENÇÃO: o name 'password_reset_confirm' deve ser exatamente este (sem namespace)
    # para que o Django consiga montar o link no e-mail de recuperação.
    path('senha/recuperar/',
         PasswordResetView.as_view(
             template_name='cardapio/password_reset_form.html',
             email_template_name='cardapio/password_reset_email.html',
             subject_template_name='cardapio/password_reset_subject.txt',
             success_url=reverse_lazy('password-reset-done'),
         ),
         name='password_reset'),
    path('senha/recuperar/enviado/',
         PasswordResetDoneView.as_view(
             template_name='cardapio/password_reset_done.html',
         ),
         name='password-reset-done'),
    # uidb64 e token são gerados pelo Django e validados na view
    path('senha/recuperar/confirmar/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='cardapio/password_reset_confirm.html',
             success_url=reverse_lazy('password-reset-complete'),
         ),
         name='password_reset_confirm'),
    path('senha/recuperar/completo/',
         PasswordResetCompleteView.as_view(
             template_name='cardapio/password_reset_complete.html',
         ),
         name='password-reset-complete'),

    # ── Troca de senha (usuário logado) ───────────────────────────────────────
    # PasswordChangeView já exige login — redireciona para LOGIN_URL se anônimo
    path('senha/alterar/',
         PasswordChangeView.as_view(
             template_name='cardapio/password_change_form.html',
             success_url=reverse_lazy('password-change-done'),
         ),
         name='password-change'),
    path('senha/alterar/concluido/',
         PasswordChangeDoneView.as_view(
             template_name='cardapio/password_change_done.html',
         ),
         name='password-change-done'),

    # ── App cardapio ──────────────────────────────────────────────────────────
    # Inclui todas as rotas do app com o namespace 'cardapio'
    path('', include('cardapio.urls')),
]
