# Formulários do app cardapio
from django import forms
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
