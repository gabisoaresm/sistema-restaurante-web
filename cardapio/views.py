# =============================================================================
# views.py — Views do app cardapio.
#
# Padrão adotado: todas as views estendem django.views.generic.base.View
# e implementam os métodos get() e/ou post() explicitamente.
# A proteção de acesso é feita por mixins herdados antes de View:
#   LoginRequiredMixin → exige usuário autenticado
#   GerenteMixin       → exige perfil 'gerente'
#   AtendenteMixin     → exige perfil 'atendente'
#   ClienteMixin       → exige perfil 'cliente'
# =============================================================================
from django.views.generic.base import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from django.db.models import Prefetch

from .models import Categoria, ItemCardapio, Perfil, Pedido, ItemPedido
from .forms import CategoriaForm, ItemCardapioForm, RegistroForm, PedidoForm


# ──────────────────────────────────────────────
# Home
# ──────────────────────────────────────────────

class HomeView(View):
    """
    Página inicial do site.
    Acesso: todos (autenticados ou não).
    Template: home.html — exibe cards diferentes conforme o perfil do usuário.
    """

    def get(self, request):
        return render(request, 'cardapio/home.html')


# ──────────────────────────────────────────────
# Mixin de autorização por perfil
# ──────────────────────────────────────────────

class GerenteMixin:
    """Redireciona para a home se o usuário logado não for gerente."""

    def dispatch(self, request, *args, **kwargs):
        # Verifica se existe perfil e se é do tipo gerente
        if not hasattr(request.user, 'perfil') or request.user.perfil.tipo != 'gerente':
            return HttpResponseRedirect(reverse_lazy('cardapio:home'))
        return super().dispatch(request, *args, **kwargs)


class AtendenteMixin:
    """Redireciona para a home se o usuário logado não for atendente."""

    def dispatch(self, request, *args, **kwargs):
        # Verifica se existe perfil e se é do tipo atendente
        if not hasattr(request.user, 'perfil') or request.user.perfil.tipo != 'atendente':
            return HttpResponseRedirect(reverse_lazy('cardapio:home'))
        return super().dispatch(request, *args, **kwargs)


class ClienteMixin:
    """Redireciona para a home se o usuário logado não for cliente."""

    def dispatch(self, request, *args, **kwargs):
        # Verifica se existe perfil e se é do tipo cliente
        if not hasattr(request.user, 'perfil') or request.user.perfil.tipo != 'cliente':
            return HttpResponseRedirect(reverse_lazy('cardapio:home'))
        return super().dispatch(request, *args, **kwargs)


# ──────────────────────────────────────────────
# CRUD de Categoria
# ──────────────────────────────────────────────

class CategoriaListView(LoginRequiredMixin, View):
    """
    Lista todas as categorias do cardápio.
    Acesso: qualquer usuário autenticado.
    Template: listaCategoria.html — botões de CRUD visíveis só para gerente.
    """

    def get(self, request):
        categorias = Categoria.objects.all()
        return render(request, 'cardapio/listaCategoria.html', {'categorias': categorias})


class CategoriaCreateView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe formulário vazio (GET) e salva nova categoria (POST).
    Acesso: gerente. Template: criaCategoria.html.
    """

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


class CategoriaUpdateView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe formulário preenchido (GET) e atualiza categoria existente (POST).
    Acesso: gerente. Template: atualizaCategoria.html.
    """

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


class CategoriaDeleteView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe página de confirmação (GET) e remove categoria (POST).
    Acesso: gerente. Template: apagaCategoria.html.
    """

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

class ItemCardapioListView(LoginRequiredMixin, View):
    """
    Lista itens do cardápio com filtro opcional por categoria (?categoria=ID).
    Acesso: qualquer usuário autenticado.
    Template: listaItemCardapio.html — botões de CRUD visíveis só para gerente.
    """

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


class ItemCardapioCreateView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe formulário vazio (GET) e salva novo item do cardápio (POST).
    Acesso: gerente. Template: criaItemCardapio.html.
    """

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


class ItemCardapioUpdateView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe formulário preenchido (GET) e atualiza item existente (POST).
    Acesso: gerente. Template: atualizaItemCardapio.html.
    """

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


class ItemCardapioDeleteView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe página de confirmação (GET) e remove item do cardápio (POST).
    Acesso: gerente. Template: apagaItemCardapio.html.
    """

    def get(self, request, pk):
        # Busca o item ou retorna 404
        item = get_object_or_404(ItemCardapio, pk=pk)
        return render(request, 'cardapio/apagaItemCardapio.html', {'item': item})

    def post(self, request, pk):
        item = get_object_or_404(ItemCardapio, pk=pk)
        item.delete()
        return HttpResponseRedirect(reverse_lazy('cardapio:lista-itens'))


# ──────────────────────────────────────────────
# Autenticação: Registro e Logout com confirmação
# ──────────────────────────────────────────────

class RegistroView(View):
    """
    Exibe formulário de registro (GET) e cria o User + Perfil ao submeter (POST).
    Acesso: qualquer visitante (não exige login).
    Template: registro.html. Redireciona para login após registro bem-sucedido.
    """

    def get(self, request):
        formulario = RegistroForm()
        return render(request, 'cardapio/registro.html', {'formulario': formulario})

    def post(self, request):
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            # Salva o User no banco
            user = formulario.save()
            # Recupera o tipo escolhido (campo extra do formulário)
            tipo = formulario.cleaned_data['tipo']
            # Cria o Perfil vinculado ao usuário recém-criado
            Perfil.objects.create(usuario=user, tipo=tipo)
            # Redireciona para a página de login
            return HttpResponseRedirect(reverse_lazy('login'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/registro.html', {'formulario': formulario})


class LogoutConfirmView(View):
    """
    Exibe página de confirmação antes de efetuar o logout (GET).
    O formulário na página faz POST para a LogoutView do Django.
    Acesso: qualquer usuário. Template: logout_confirma.html.
    """

    def get(self, request):
        return render(request, 'cardapio/logout_confirma.html')


# ──────────────────────────────────────────────
# Pedidos do cliente
# ──────────────────────────────────────────────

class CriarPedidoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe os itens disponíveis agrupados por categoria (GET) e cria um
    novo Pedido com seus ItensPedido ao submeter (POST).
    Acesso: cliente. Template: criarPedido.html.
    Os itens são enviados como campos 'item_ID' no POST; a view itera
    sobre eles e cria um ItemPedido para cada quantidade > 0.
    """

    def get(self, request):
        # Categorias com seus itens disponíveis pré-carregados (evita N+1 queries)
        categorias = Categoria.objects.prefetch_related(
            Prefetch(
                'itemcardapio_set',
                queryset=ItemCardapio.objects.filter(disponivel=True),
                to_attr='itens_disponiveis',
            )
        )
        formulario = PedidoForm()
        return render(request, 'cardapio/criarPedido.html', {
            'categorias': categorias,
            'formulario': formulario,
        })

    def post(self, request):
        formulario = PedidoForm(request.POST)

        # Coleta os itens selecionados: campos cujo nome começa com "item_"
        itens_pedido = []
        for chave, valor in request.POST.items():
            if chave.startswith('item_'):
                try:
                    item_id = int(chave[5:])   # remove o prefixo "item_"
                    quantidade = int(valor)
                    if quantidade > 0:
                        item = ItemCardapio.objects.get(pk=item_id, disponivel=True)
                        itens_pedido.append((item, quantidade))
                except (ValueError, ItemCardapio.DoesNotExist):
                    pass  # ignora campos inválidos ou itens indisponíveis

        if not itens_pedido:
            # Nenhum item selecionado: reexibe o formulário com aviso
            categorias = Categoria.objects.prefetch_related(
                Prefetch(
                    'itemcardapio_set',
                    queryset=ItemCardapio.objects.filter(disponivel=True),
                    to_attr='itens_disponiveis',
                )
            )
            return render(request, 'cardapio/criarPedido.html', {
                'categorias': categorias,
                'formulario': formulario,
                'erro': 'Selecione pelo menos um item com quantidade maior que zero.',
            })

        if formulario.is_valid():
            # Cria o pedido vinculado ao cliente logado
            pedido = Pedido.objects.create(
                cliente=request.user,
                status='recebido',
                observacoes=formulario.cleaned_data.get('observacoes') or '',
            )
            # Cria um ItemPedido para cada item selecionado
            for item, quantidade in itens_pedido:
                ItemPedido.objects.create(pedido=pedido, item=item, quantidade=quantidade)

            return HttpResponseRedirect(reverse_lazy('cardapio:meus-pedidos'))

        # Formulário inválido: reexibe com erros
        categorias = Categoria.objects.prefetch_related(
            Prefetch(
                'itemcardapio_set',
                queryset=ItemCardapio.objects.filter(disponivel=True),
                to_attr='itens_disponiveis',
            )
        )
        return render(request, 'cardapio/criarPedido.html', {
            'categorias': categorias,
            'formulario': formulario,
        })


class MeusPedidosView(LoginRequiredMixin, ClienteMixin, View):
    """
    Lista os pedidos do cliente logado com itens e totais calculados.
    Acesso: cliente. Template: meusPedidos.html.
    Os totais são calculados na view (templates não fazem multiplicação).
    """

    def get(self, request):
        # Busca os pedidos do cliente com itens pré-carregados (evita N+1 queries)
        pedidos_qs = Pedido.objects.filter(cliente=request.user).prefetch_related(
            'itens__item'
        )

        # Calcula subtotal por item e total do pedido na view (templates não fazem multiplicação)
        pedidos = []
        for pedido in pedidos_qs:
            itens_com_subtotal = []
            total = 0
            for ip in pedido.itens.all():
                subtotal = ip.quantidade * ip.item.preco
                total += subtotal
                itens_com_subtotal.append({'ip': ip, 'subtotal': subtotal})
            pedidos.append({'pedido': pedido, 'itens': itens_com_subtotal, 'total': total})

        return render(request, 'cardapio/meusPedidos.html', {'pedidos': pedidos})


# ──────────────────────────────────────────────
# Fila de pedidos do atendente
# ──────────────────────────────────────────────

class FilaPedidosView(LoginRequiredMixin, AtendenteMixin, View):
    """
    Exibe pedidos pendentes (não entregues) para o atendente (GET).
    Aceita filtro por status via ?status=VALOR para ver qualquer etapa.
    Acesso: atendente. Template: filaPedidos.html.
    """

    # Status disponíveis para filtro — espelha o modelo Pedido
    STATUS_CHOICES = Pedido.STATUS_CHOICES

    def get(self, request):
        # Filtro opcional por status via query string (?status=VALOR)
        status_filtro = request.GET.get('status')

        if status_filtro:
            pedidos_qs = Pedido.objects.filter(status=status_filtro)
        else:
            # Padrão: exibe todos os pedidos que ainda não foram entregues
            pedidos_qs = Pedido.objects.exclude(status='entregue')

        # Pré-carrega os itens de cada pedido (evita N+1 queries)
        pedidos_qs = pedidos_qs.prefetch_related('itens__item')

        return render(request, 'cardapio/filaPedidos.html', {
            'pedidos': pedidos_qs,
            'status_choices': self.STATUS_CHOICES,
            'status_filtro': status_filtro,
        })


class AtualizarStatusPedidoView(LoginRequiredMixin, AtendenteMixin, View):
    """
    Atualiza o status de um pedido via POST e redireciona para a fila.
    Valida que o status recebido é um valor permitido (STATUS_VALIDOS)
    antes de salvar, evitando valores arbitrários do POST.
    Acesso: atendente. Não possui template próprio (só post).
    """

    # Status válidos — evita gravar valores arbitrários do POST
    STATUS_VALIDOS = {choice[0] for choice in Pedido.STATUS_CHOICES}

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        novo_status = request.POST.get('status')

        # Só atualiza se o valor recebido for um status válido
        if novo_status in self.STATUS_VALIDOS:
            pedido.status = novo_status
            pedido.save()

        return HttpResponseRedirect(reverse_lazy('cardapio:fila-pedidos'))


# ──────────────────────────────────────────────
# Painel de pedidos do gerente
# ──────────────────────────────────────────────

class PainelGerenteView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe todos os pedidos em tabela para o gerente (GET).
    Aceita filtros combinados: ?status=VALOR e ?data=AAAA-MM-DD.
    Calcula o total de cada pedido na view (templates não fazem multiplicação).
    Acesso: gerente. Template: painelGerente.html.
    """

    def get(self, request):
        pedidos_qs = Pedido.objects.prefetch_related('itens__item').select_related('cliente')

        # Filtro por status via query string (?status=VALOR)
        status_filtro = request.GET.get('status')
        if status_filtro:
            pedidos_qs = pedidos_qs.filter(status=status_filtro)

        # Filtro por data via query string (?data=AAAA-MM-DD)
        data_filtro = request.GET.get('data')
        if data_filtro:
            pedidos_qs = pedidos_qs.filter(data_hora__date=data_filtro)

        # Calcula o total de cada pedido na view (templates não fazem multiplicação)
        pedidos = []
        for pedido in pedidos_qs:
            total = sum(ip.quantidade * ip.item.preco for ip in pedido.itens.all())
            pedidos.append({'pedido': pedido, 'total': total})

        return render(request, 'cardapio/painelGerente.html', {
            'pedidos': pedidos,
            'status_choices': Pedido.STATUS_CHOICES,
            'status_filtro': status_filtro,
            'data_filtro': data_filtro or '',
        })
