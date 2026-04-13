# =============================================================================
# forms.py — Formulários do app cardapio.
#
# Cada formulário corresponde a uma operação do sistema:
#   CategoriaForm      → criar/editar categorias do cardápio
#   ItemCardapioForm   → criar/editar itens do cardápio
#   PedidoForm         → campo de observações ao criar um pedido
#   RegistroForm       → cadastro de novo usuário com escolha de perfil
# =============================================================================

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Categoria, ItemCardapio, Pedido


# ── Formulários do cardápio ───────────────────────────────────────────────────

class CategoriaForm(forms.ModelForm):
    """
    Formulário para criação e edição de categorias do cardápio.
    Expõe todos os campos do modelo Categoria.
    """
    class Meta:
        model = Categoria
        fields = '__all__'


class ItemCardapioForm(forms.ModelForm):
    """
    Formulário para criação e edição de itens do cardápio.
    Expõe todos os campos do modelo ItemCardapio (nome, descrição,
    preço, categoria e disponibilidade).
    """
    class Meta:
        model = ItemCardapio
        fields = '__all__'


# ── Formulários de pedido ─────────────────────────────────────────────────────

class PedidoForm(forms.ModelForm):
    """
    Formulário para criação de pedido pelo cliente.
    Expõe apenas o campo de observações — cliente, status e data_hora
    são preenchidos automaticamente na view CriarPedidoView.
    Os itens selecionados são lidos diretamente do POST (campos item_ID).
    """
    class Meta:
        model = Pedido
        fields = ['observacoes']
        widgets = {
            # Textarea menor para melhor layout na página de pedido
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'observacoes': 'Observações (opcional)',
        }


# ── Formulário de autenticação ────────────────────────────────────────────────

class RegistroForm(UserCreationForm):
    """
    Formulário de registro de novo usuário com escolha do tipo de perfil.
    Estende o UserCreationForm do Django com o campo extra 'tipo'.
    O campo 'tipo' não pertence ao modelo User — é processado na
    RegistroView para criar o objeto Perfil vinculado ao usuário.
    """

    # Opções de tipo de perfil — espelha as choices do modelo Perfil
    TIPO_CHOICES = [
        ('gerente', 'Gerente'),
        ('atendente', 'Atendente'),
        ('cliente', 'Cliente'),
    ]

    # Campo extra: não entra em Meta.fields — tratado separadamente na view
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label='Tipo de perfil')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
