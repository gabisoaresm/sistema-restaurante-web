# Formulários do app cardapio
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Categoria, ItemCardapio


class CategoriaForm(forms.ModelForm):
    """Formulário para criação e edição de categorias do cardápio."""
    class Meta:
        model = Categoria
        fields = '__all__'


class ItemCardapioForm(forms.ModelForm):
    """Formulário para criação e edição de itens do cardápio."""
    class Meta:
        model = ItemCardapio
        fields = '__all__'


class RegistroForm(UserCreationForm):
    """Formulário de registro de novo usuário com escolha do tipo de perfil."""

    # Opções de tipo de perfil — espelha as choices do modelo Perfil
    TIPO_CHOICES = [
        ('gerente', 'Gerente'),
        ('atendente', 'Atendente'),
        ('cliente', 'Cliente'),
    ]

    # Campo extra: não pertence ao User, será usado na view para criar o Perfil
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label='Tipo de perfil')

    class Meta:
        model = User
        # 'tipo' não entra aqui — é tratado separadamente na view
        fields = ('username', 'password1', 'password2')
