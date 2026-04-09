# Formulários do app cardapio
from django import forms
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    """Formulário para criação e edição de categorias do cardápio."""
    class Meta:
        model = Categoria
        fields = '__all__'
