# Views do app cardapio — padrão da aula: classes que estendem View
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Categoria, ItemCardapio
from .forms import CategoriaForm, ItemCardapioForm


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


# ──────────────────────────────────────────────
# CRUD de ItemCardapio
# ──────────────────────────────────────────────

class ItemCardapioListView(View):
    """Lista itens do cardápio, com filtro opcional por categoria via GET ?categoria=ID."""

    def get(self, request):
        # Verifica se foi passado filtro de categoria na query string
        categoria_id = request.GET.get('categoria')
        if categoria_id:
            itens = ItemCardapio.objects.filter(categoria_id=categoria_id)
        else:
            itens = ItemCardapio.objects.all()

        # Passa todas as categorias para montar os links de filtro no template
        categorias = Categoria.objects.all()
        return render(request, 'cardapio/listaItemCardapio.html', {
            'itens': itens,
            'categorias': categorias,
            'categoria_selecionada': categoria_id,
        })


class ItemCardapioCreateView(View):
    """Exibe formulário vazio e salva novo item do cardápio."""

    def get(self, request):
        # Formulário vazio para criação
        formulario = ItemCardapioForm()
        return render(request, 'cardapio/criaItemCardapio.html', {'formulario': formulario})

    def post(self, request):
        formulario = ItemCardapioForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect(reverse_lazy('cardapio:lista-itens'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/criaItemCardapio.html', {'formulario': formulario})


class ItemCardapioUpdateView(View):
    """Exibe formulário preenchido e atualiza item existente."""

    def get(self, request, pk):
        # Busca o item ou retorna 404
        item = get_object_or_404(ItemCardapio, pk=pk)
        formulario = ItemCardapioForm(instance=item)
        return render(request, 'cardapio/atualizaItemCardapio.html', {'formulario': formulario, 'item': item})

    def post(self, request, pk):
        item = get_object_or_404(ItemCardapio, pk=pk)
        formulario = ItemCardapioForm(request.POST, instance=item)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect(reverse_lazy('cardapio:lista-itens'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/atualizaItemCardapio.html', {'formulario': formulario, 'item': item})


class ItemCardapioDeleteView(View):
    """Exibe confirmação e remove item do cardápio."""

    def get(self, request, pk):
        # Busca o item ou retorna 404
        item = get_object_or_404(ItemCardapio, pk=pk)
        return render(request, 'cardapio/apagaItemCardapio.html', {'item': item})

    def post(self, request, pk):
        item = get_object_or_404(ItemCardapio, pk=pk)
        item.delete()
        return HttpResponseRedirect(reverse_lazy('cardapio:lista-itens'))
