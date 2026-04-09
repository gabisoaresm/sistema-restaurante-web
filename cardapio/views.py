# Views do app cardapio — padrão da aula: classes que estendem View
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Categoria
from .forms import CategoriaForm


# ──────────────────────────────────────────────
# Home
# ──────────────────────────────────────────────

class HomeView(View):
    """Página inicial do site."""

    def get(self, request):
        return render(request, 'cardapio/home.html')


# ──────────────────────────────────────────────
# CRUD de Categoria
# ──────────────────────────────────────────────

class CategoriaListView(View):
    """Lista todas as categorias do cardápio."""

    def get(self, request):
        categorias = Categoria.objects.all()
        return render(request, 'cardapio/listaCategoria.html', {'categorias': categorias})


class CategoriaCreateView(View):
    """Exibe formulário vazio e salva nova categoria."""

    def get(self, request):
        # Formulário vazio para criação
        formulario = CategoriaForm()
        return render(request, 'cardapio/criaCategoria.html', {'formulario': formulario})

    def post(self, request):
        formulario = CategoriaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect(reverse_lazy('cardapio:lista-categorias'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/criaCategoria.html', {'formulario': formulario})


class CategoriaUpdateView(View):
    """Exibe formulário preenchido e atualiza categoria existente."""

    def get(self, request, pk):
        # Busca a categoria ou retorna 404
        categoria = get_object_or_404(Categoria, pk=pk)
        formulario = CategoriaForm(instance=categoria)
        return render(request, 'cardapio/atualizaCategoria.html', {'formulario': formulario, 'categoria': categoria})

    def post(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        formulario = CategoriaForm(request.POST, instance=categoria)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect(reverse_lazy('cardapio:lista-categorias'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/atualizaCategoria.html', {'formulario': formulario, 'categoria': categoria})


class CategoriaDeleteView(View):
    """Exibe confirmação e remove categoria."""

    def get(self, request, pk):
        # Busca a categoria ou retorna 404
        categoria = get_object_or_404(Categoria, pk=pk)
        return render(request, 'cardapio/apagaCategoria.html', {'categoria': categoria})

    def post(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        categoria.delete()
        return HttpResponseRedirect(reverse_lazy('cardapio:lista-categorias'))
