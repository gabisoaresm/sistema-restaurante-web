# =============================================================================
# forms.py — Formulários do app cardapio.
#
# Cada formulário corresponde a uma operação do sistema:
#   CategoriaForm            → criar/editar categorias do cardápio
#   ItemCardapioForm         → criar/editar itens do cardápio
#   PagamentoCartaoSalvoForm → selecionar cartão salvo e informar CVV no pagamento
#   CartaoForm               → cadastrar novo cartão salvo pelo cliente
#   RegistroForm             → cadastro de novo usuário (sempre como cliente)
#   AlterarPerfilForm        → alterar o tipo de perfil de um usuário (gerente)
#   PerfilUsuarioForm        → edição dos dados pessoais do usuário logado
# =============================================================================

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Categoria, ItemCardapio, CartaoSalvo


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


# ── Formulário de pagamento com cartão salvo ─────────────────────────────────

class PagamentoCartaoSalvoForm(forms.Form):
    """
    Formulário de pagamento com cartão salvo.
    Usado na tela de criação de pedido para o cliente escolher um cartão
    e informar o CVV para confirmar o pagamento.
    O queryset de cartao é sobrescrito na view para mostrar apenas
    os cartões do usuário logado.
    """

    cartao = forms.ModelChoiceField(
        queryset=CartaoSalvo.objects.none(),  # filtrado por usuário na view
        label='Cartão',
        empty_label='— Selecione um cartão —',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    cvv = forms.CharField(
        max_length=4,
        label='CVV',
        help_text='Informe o CVV do cartão para confirmar',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'CVV',
            'inputmode': 'numeric',
            'style': 'width: 80px',
        }),
    )


# ── Formulário de cartão salvo ────────────────────────────────────────────────

class CartaoForm(forms.Form):
    """
    Formulário para cadastro de novo cartão salvo pelo cliente.
    O número completo (numero_cartao) é usado apenas para extrair os últimos
    4 dígitos e gerar numero_mascarado — nunca é persistido no banco.
    O CVV é salvo para validação posterior no momento do pagamento.
    """

    BANDEIRA_CHOICES = [
        ('visa',       'Visa'),
        ('mastercard', 'Mastercard'),
        ('elo',        'Elo'),
        ('amex',       'American Express'),
    ]
    TIPO_CHOICES = [
        ('credito', 'Crédito'),
        ('debito',  'Débito'),
    ]

    apelido      = forms.CharField(max_length=50, label='Apelido',
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    nome_titular = forms.CharField(max_length=200, label='Nome do titular',
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero_cartao = forms.CharField(
        max_length=16,
        label='Número do cartão',
        help_text='Apenas números, sem espaços',
        widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric'}),
    )
    bandeira = forms.ChoiceField(choices=BANDEIRA_CHOICES, label='Bandeira',
                                 widget=forms.Select(attrs={'class': 'form-select'}))
    tipo     = forms.ChoiceField(choices=TIPO_CHOICES, label='Tipo',
                                 widget=forms.Select(attrs={'class': 'form-select'}))
    validade = forms.CharField(max_length=7, label='Validade', help_text='MM/AAAA',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AAAA'}))
    cvv      = forms.CharField(max_length=4, label='CVV',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'style': 'width: 100px'}))


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
