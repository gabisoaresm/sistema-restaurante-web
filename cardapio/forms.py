# =============================================================================
# forms.py — Formulários do app cardapio.
#
# Cada formulário corresponde a uma operação do sistema:
#   CategoriaForm      → criar/editar categorias do cardápio
#   ItemCardapioForm   → criar/editar itens do cardápio
#   PedidoForm         → campo de observações ao criar um pedido
#   RegistroForm       → cadastro de novo usuário (sempre como cliente)
#   PerfilUsuarioForm  → edição dos dados pessoais do usuário logado
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


# ── Formulários de autenticação e perfil ─────────────────────────────────────

class RegistroForm(UserCreationForm):
    """
    Formulário de registro de novo usuário.
    Todo usuário registrado pelo site é automaticamente cliente —
    não há campo de escolha de perfil por segurança.
    O campo email é obrigatório aqui, embora seja opcional no model User.
    """

    # email sobrescrito para torná-lo obrigatório no registro
    email = forms.EmailField(required=True, label='E-mail')

    def clean_email(self):
        # Normaliza para minúsculas antes de comparar
        email = self.cleaned_data['email'].lower()
        # Verifica se já existe outro usuário com esse e-mail (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este e-mail.')
        return email

    class Meta:
        model = User
        # first_name e last_name são opcionais no model (blank=True)
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class AlterarPerfilForm(forms.Form):
    """
    Formulário simples para o gerente alterar o tipo de perfil de outro usuário.
    Não é um ModelForm — o campo tipo é aplicado manualmente na view
    sobre o objeto Perfil do usuário selecionado.
    """

    TIPO_CHOICES = [
        ('gerente',   'Gerente'),
        ('atendente', 'Atendente'),
        ('cliente',   'Cliente'),
    ]

    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label='Tipo de perfil')


class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário para edição dos dados pessoais do usuário logado.
    Permite alterar nome, sobrenome e e-mail — não altera senha nem username.
    Usado na PerfilView com instance=request.user para garantir que
    o usuário só edita seus próprios dados.
    """

    # email sobrescrito para torná-lo obrigatório na edição do perfil
    email = forms.EmailField(required=True, label='E-mail')

    def clean_email(self):
        # Normaliza para minúsculas antes de comparar
        email = self.cleaned_data['email'].lower()
        # Exclui o próprio usuário da verificação — sem isso ele não conseguiria
        # salvar o perfil sem trocar o e-mail, pois o seu próprio já estaria no banco
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este e-mail.')
        return email

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name':  'Sobrenome',
        }
