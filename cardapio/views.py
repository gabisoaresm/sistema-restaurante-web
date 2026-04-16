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
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.forms import PasswordResetForm

from django.db.models import Prefetch

from django.contrib.auth.models import User
from .models import Categoria, ItemCardapio, Perfil, Pedido, ItemPedido, CartaoSalvo
from .forms import (
    CategoriaForm, ItemCardapioForm, RegistroForm,
    PedidoForm, PerfilUsuarioForm, AlterarPerfilForm,
    CartaoForm, PagamentoCartaoSalvoForm,
)


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
        # Atendente não tem home — vai direto para a Fila de Pedidos
        if request.user.is_authenticated and hasattr(request.user, 'perfil') \
                and request.user.perfil.tipo == 'atendente':
            return redirect(reverse_lazy('cardapio:fila-pedidos'))
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
# Redirecionamento pós-login
# ──────────────────────────────────────────────

class RedirecionarAposLoginView(LoginRequiredMixin, View):
    """
    View de redirecionamento pós-login.
    Verifica o perfil do usuário e envia para a página inicial adequada ao seu tipo.
    Atendente vai direto para a Fila de Pedidos; demais perfis vão para a Home.
    """

    def get(self, request):
        try:
            tipo = request.user.perfil.tipo
        except AttributeError:
            # Usuário sem perfil cadastrado — fallback seguro para a Home
            return redirect(reverse_lazy('cardapio:home'))

        if tipo == 'atendente':
            return redirect(reverse_lazy('cardapio:fila-pedidos'))

        # gerente e cliente vão para a Home
        return redirect(reverse_lazy('cardapio:home'))


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
# Cardápio para o cliente (com seleção de itens)
# ──────────────────────────────────────────────

class CardapioClienteView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe o cardápio agrupado por categoria para o cliente.
    O cliente ajusta as quantidades via <input type="number"> e submete o formulário
    ao clicar em "Criar Pedido". Não há recarregamento a cada clique.
    O estado do carrinho é armazenado em request.session['carrinho'] como
    um dicionário {'<item_id>': quantidade}.
    Acesso: cliente autenticado. Template: cardapioCliente.html.
    """

    def get(self, request):
        # Lê o carrinho atual da sessão (dicionário vazio se ainda não existir)
        carrinho = request.session.get('carrinho', {})

        # Monta a lista de categorias com seus itens disponíveis e quantidades do carrinho
        categorias_ctx = self._montar_categorias(carrinho)

        # Soma total de itens no carrinho para exibir no rodapé
        total_itens = sum(carrinho.values()) if carrinho else 0

        return render(request, 'cardapio/cardapioCliente.html', {
            'categorias_ctx': categorias_ctx,
            'total_itens': total_itens,
        })

    def post(self, request):
        # Lê os campos do formulário com prefixo 'item_' (ex.: item_3 = 2)
        novo_carrinho = {}
        for chave, valor in request.POST.items():
            if chave.startswith('item_'):
                item_id = chave[len('item_'):]  # extrai o id numérico como string
                try:
                    quantidade = max(0, int(valor))
                except (ValueError, TypeError):
                    quantidade = 0
                # Só inclui no carrinho itens com quantidade maior que zero
                if quantidade > 0:
                    novo_carrinho[item_id] = quantidade

        # Salva o carrinho atualizado na sessão e marca como modificado
        request.session['carrinho'] = novo_carrinho
        request.session.modified = True

        # Redireciona para a página do carrinho/pedido
        return HttpResponseRedirect(reverse_lazy('cardapio:pedido-carrinho'))

    def _montar_categorias(self, carrinho):
        """Constrói o contexto de categorias com itens disponíveis e quantidades."""
        categorias_ctx = []
        for categoria in Categoria.objects.all():
            itens_disponiveis = categoria.itemcardapio_set.filter(disponivel=True)

            # Ignora categorias sem nenhum item disponível
            if not itens_disponiveis.exists():
                continue

            # Para cada item, inclui a quantidade atual no carrinho (0 se não estiver)
            itens_ctx = [
                {
                    'item': item,
                    'quantidade': carrinho.get(str(item.id), 0),
                }
                for item in itens_disponiveis
            ]

            categorias_ctx.append({
                'categoria': categoria,
                'itens': itens_ctx,
            })

        return categorias_ctx


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
            # Todo usuário registrado pelo site é automaticamente cliente
            Perfil.objects.create(usuario=user, tipo='cliente')
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


class PerfilView(LoginRequiredMixin, View):
    """
    Exibe informações do usuário logado e formulário para editar
    nome, sobrenome e e-mail (GET).
    Salva as alterações garantindo instance=request.user —
    o usuário só edita seus próprios dados (POST).
    Após salvar com sucesso, reexibe a página com mensagem de confirmação.
    """

    def get(self, request):
        # Pré-preenche o formulário com os dados do usuário logado
        formulario = PerfilUsuarioForm(instance=request.user)
        return render(request, 'cardapio/perfil.html', {'formulario': formulario})

    def post(self, request):
        # instance=request.user garante que o usuário edita apenas seus próprios dados
        formulario = PerfilUsuarioForm(request.POST, instance=request.user)
        if formulario.is_valid():
            formulario.save()
            return render(request, 'cardapio/perfil.html', {
                'formulario': formulario,
                'sucesso': 'Dados atualizados com sucesso!',
            })
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/perfil.html', {'formulario': formulario})


# ──────────────────────────────────────────────
# Gerenciamento de usuários (gerente)
# ──────────────────────────────────────────────

class GerenciarUsuariosView(LoginRequiredMixin, GerenteMixin, View):
    """
    Lista todos os usuários cadastrados no sistema com seu perfil (GET).
    Acesso: gerente. Template: gerenciarUsuarios.html.
    """

    def get(self, request):
        # Exclui superusuários e usuários sem Perfil (ex.: admin criado via createsuperuser)
        # select_related('perfil') evita N+1 queries ao acessar usuario.perfil no template
        usuarios = (
            User.objects
            .filter(perfil__isnull=False, is_superuser=False)
            .select_related('perfil')
            .order_by('username')
        )
        return render(request, 'cardapio/gerenciarUsuarios.html', {'usuarios': usuarios})


class AlterarPerfilUsuarioView(LoginRequiredMixin, GerenteMixin, View):
    """
    Exibe formulário para alterar o tipo de perfil de um usuário (GET).
    Salva o novo tipo e redireciona para a lista de usuários (POST).
    Acesso: gerente. Template: alterarPerfilUsuario.html.
    """

    def get(self, request, pk):
        # Busca o usuário alvo ou retorna 404
        usuario = get_object_or_404(User, pk=pk)
        # Proteção: usuário sem Perfil não pode ser editado por esta view
        if not hasattr(usuario, 'perfil'):
            return redirect('cardapio:gerenciar-usuarios')
        # Pré-seleciona o tipo atual no formulário
        formulario = AlterarPerfilForm(initial={'tipo': usuario.perfil.tipo})
        return render(request, 'cardapio/alterarPerfilUsuario.html', {
            'usuario': usuario,
            'formulario': formulario,
        })

    def post(self, request, pk):
        usuario = get_object_or_404(User, pk=pk)
        # Proteção: usuário sem Perfil não pode ser editado por esta view
        if not hasattr(usuario, 'perfil'):
            return redirect('cardapio:gerenciar-usuarios')
        formulario = AlterarPerfilForm(request.POST)
        if formulario.is_valid():
            # Atualiza o tipo do Perfil vinculado ao usuário selecionado
            usuario.perfil.tipo = formulario.cleaned_data['tipo']
            usuario.perfil.save()
            return HttpResponseRedirect(reverse_lazy('cardapio:gerenciar-usuarios'))
        # Formulário inválido: reexibe com erros
        return render(request, 'cardapio/alterarPerfilUsuario.html', {
            'usuario': usuario,
            'formulario': formulario,
        })


# ──────────────────────────────────────────────
# Recuperação de senha — override para link legível no console
# ──────────────────────────────────────────────

class ConsolePasswordResetForm(PasswordResetForm):
    """
    Sobrescreve send_mail() do PasswordResetForm para imprimir o link de
    recuperação de forma legível no console durante o desenvolvimento.

    O console.EmailBackend usa codificação quoted-printable (QP), que quebra
    URLs longas com =\\n a cada 76 caracteres — impossibilitando a cópia.
    Este override imprime o link sem codificação após o envio normal do e-mail.

    ATENÇÃO: o send_mail que o Django chama pertence ao FORMULÁRIO, não à view.
    Sobrescrever send_mail() na view não tem efeito — por isso usamos o formulário.
    """
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        # Envia o e-mail normalmente (aparece no console com QP encoding)
        super().send_mail(
            subject_template_name, email_template_name, context,
            from_email, to_email, html_email_template_name,
        )
        # Imprime o link limpo e copiável no terminal
        link = '{protocol}://{domain}{path}'.format(
            protocol=context['protocol'],
            domain=context['domain'],
            path=reverse('password_reset_confirm',
                         kwargs={'uidb64': context['uid'], 'token': context['token']}),
        )
        print('\n' + '=' * 70)
        print('LINK DE RECUPERAÇÃO DE SENHA (copie e cole no navegador):')
        print(link)
        print('=' * 70 + '\n')


class PasswordResetView(DjangoPasswordResetView):
    """
    Usa ConsolePasswordResetForm em vez do formulário padrão do Django,
    para que o link de recuperação seja impresso de forma legível no console.
    """
    form_class = ConsolePasswordResetForm


# ──────────────────────────────────────────────
# Pedidos do cliente — fluxo carrinho (Fase 2)
# ──────────────────────────────────────────────

class PedidoCarrinhoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe o resumo do carrinho (GET) e processa o pagamento com cartão salvo (POST).
    Os itens do pedido vêm de request.session['carrinho'] — preenchido em CardapioClienteView.
    O pedido só é criado após validação do CVV; em caso de erro, a página é reexibida.
    Acesso: cliente autenticado. Template: pedidoCarrinho.html.
    """

    def get(self, request):
        # Lê o carrinho da sessão
        carrinho = request.session.get('carrinho', {})

        # Se o carrinho estiver vazio, renderiza página informando o cliente
        if not carrinho:
            return render(request, 'cardapio/pedidoCarrinho.html', {'carrinho_vazio': True})

        # Monta lista de itens com subtotal calculado na view (templates não multiplicam)
        itens_pedido, total = self._montar_itens(carrinho)

        # Formulário de cartão com queryset filtrado para o usuário logado
        form_cartao = self._form_cartao(request)

        return render(request, 'cardapio/pedidoCarrinho.html', {
            'carrinho_vazio': False,
            'itens_pedido':   itens_pedido,
            'total':          total,
            'form_cartao':    form_cartao,
            'cartoes':        request.user.cartoes.all(),
        })

    def post(self, request):
        carrinho = request.session.get('carrinho', {})

        # Carrinho vazio: não há pedido para criar
        if not carrinho:
            return HttpResponseRedirect(reverse_lazy('cardapio:cardapio-cliente'))

        # Monta itens e total a partir do carrinho
        itens_pedido, total = self._montar_itens(carrinho)

        # Lê observações do POST (campo opcional)
        observacoes = request.POST.get('observacoes', '').strip()

        # Valida o formulário de cartão + CVV
        form_cartao = self._form_cartao(request, data=request.POST)

        if not form_cartao.is_valid():
            # Reexibe o formulário com os erros de validação do Django
            return render(request, 'cardapio/pedidoCarrinho.html', {
                'carrinho_vazio': False,
                'itens_pedido':   itens_pedido,
                'total':          total,
                'form_cartao':    form_cartao,
                'cartoes':        request.user.cartoes.all(),
            })

        cartao       = form_cartao.cleaned_data['cartao']
        cvv_digitado = form_cartao.cleaned_data['cvv']

        # Segurança: confirma que o cartão pertence ao usuário logado
        if cartao.usuario != request.user:
            return render(request, 'cardapio/pedidoCarrinho.html', {
                'carrinho_vazio': False,
                'itens_pedido':   itens_pedido,
                'total':          total,
                'form_cartao':    form_cartao,
                'cartoes':        request.user.cartoes.all(),
                'erro_cvv':       'Cartão inválido.',
            })

        # Valida o CVV digitado contra o CVV salvo no cartão
        if cartao.cvv != cvv_digitado:
            return render(request, 'cardapio/pedidoCarrinho.html', {
                'carrinho_vazio': False,
                'itens_pedido':   itens_pedido,
                'total':          total,
                'form_cartao':    form_cartao,
                'cartoes':        request.user.cartoes.all(),
                'erro_cvv':       'CVV incorreto. Tente novamente.',
            })

        # Determina a forma de pagamento conforme o tipo do cartão
        forma = 'cartao_credito' if cartao.tipo == 'credito' else 'cartao_debito'

        # Cria o pedido com status pago (pagamento realizado agora)
        pedido = Pedido.objects.create(
            cliente=request.user,
            status='recebido',
            observacoes=observacoes,
            forma_pagamento=forma,
            status_pagamento='pago',
            cartao_utilizado=cartao,
        )

        # Cria um ItemPedido para cada item do carrinho
        for entrada in itens_pedido:
            ItemPedido.objects.create(
                pedido=pedido,
                item=entrada['item'],
                quantidade=entrada['quantidade'],
            )

        # Limpa o carrinho da sessão após criação bem-sucedida do pedido
        request.session['carrinho'] = {}
        request.session.modified = True

        # Redireciona para a página de confirmação com o id do pedido criado
        return HttpResponseRedirect(
            reverse('cardapio:pedido-confirmado', kwargs={'pk': pedido.pk})
        )

    # ── Métodos auxiliares ────────────────────────────────────────────────────

    def _montar_itens(self, carrinho):
        """
        Recebe o dicionário de carrinho {str(item_id): quantidade} e retorna
        uma lista de dicts {'item', 'quantidade', 'subtotal'} e o total geral.
        Usa get_object_or_404 para cada item_id do carrinho.
        """
        itens_pedido = []
        total = 0
        for item_id_str, quantidade in carrinho.items():
            item = get_object_or_404(ItemCardapio, pk=int(item_id_str))
            subtotal = item.preco * quantidade
            total += subtotal
            itens_pedido.append({
                'item':       item,
                'quantidade': quantidade,
                'subtotal':   subtotal,
            })
        return itens_pedido, total

    def _form_cartao(self, request, data=None):
        """Cria PagamentoCartaoSalvoForm com queryset filtrado para o usuário logado."""
        form = PagamentoCartaoSalvoForm(data)
        form.fields['cartao'].queryset = CartaoSalvo.objects.filter(usuario=request.user)
        return form


class PedidoConfirmadoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe a confirmação do pedido criado pela PedidoCarrinhoView.
    Verifica que o pedido pertence ao usuário logado antes de renderizar.
    Acesso: cliente autenticado. Template: pedidoConfirmado.html.
    """

    def get(self, request, pk):
        # Busca o pedido ou retorna 404
        pedido = get_object_or_404(Pedido, pk=pk)

        # Segurança: impede que um cliente veja o pedido de outro
        if pedido.cliente != request.user:
            return HttpResponseRedirect(reverse_lazy('cardapio:home'))

        # Busca os itens com subtotal calculado na view
        itens_confirmados = []
        total = 0
        for ip in pedido.itens.select_related('item').all():
            subtotal = ip.quantidade * ip.item.preco
            total += subtotal
            itens_confirmados.append({'ip': ip, 'subtotal': subtotal})

        return render(request, 'cardapio/pedidoConfirmado.html', {
            'pedido':            pedido,
            'itens_confirmados': itens_confirmados,
            'total':             total,
        })


# ──────────────────────────────────────────────
# Pedidos do cliente — fluxo legado (mantido para referência)
# ──────────────────────────────────────────────

class CriarPedidoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe os itens disponíveis agrupados por categoria e formulário de pagamento (GET).
    Cria o Pedido SOMENTE se o pagamento for confirmado via cartão (POST).

    Cartão: POST com pagar_cartao — valida CVV do cartão salvo.

    Acesso: cliente. Template: criarPedido.html.
    """

    def _carregar_categorias(self):
        """Retorna categorias com itens disponíveis pré-carregados (evita N+1 queries)."""
        return Categoria.objects.prefetch_related(
            Prefetch(
                'itemcardapio_set',
                queryset=ItemCardapio.objects.filter(disponivel=True),
                to_attr='itens_disponiveis',
            )
        )

    def _form_cartao_salvo(self, request, data=None):
        """Cria PagamentoCartaoSalvoForm com queryset filtrado para o usuário logado."""
        form = PagamentoCartaoSalvoForm(data)
        form.fields['cartao'].queryset = CartaoSalvo.objects.filter(usuario=request.user)
        return form

    def get(self, request):
        return render(request, 'cardapio/criarPedido.html', {
            'categorias':      self._carregar_categorias(),
            'formulario':      PedidoForm(),
            'form_cartao_salvo': self._form_cartao_salvo(request),
            'cartoes_usuario': CartaoSalvo.objects.filter(usuario=request.user),
        })

    def post(self, request):
        formulario   = PedidoForm(request.POST)
        form_cartao  = self._form_cartao_salvo(request, data=request.POST)

        # Coleta os itens selecionados: campos cujo nome começa com "item_"
        itens_pedido = []
        for chave, valor in request.POST.items():
            if chave.startswith('item_'):
                try:
                    item_id   = int(chave[5:])   # remove o prefixo "item_"
                    quantidade = int(valor)
                    if quantidade > 0:
                        item = ItemCardapio.objects.get(pk=item_id, disponivel=True)
                        itens_pedido.append((item, quantidade))
                except (ValueError, ItemCardapio.DoesNotExist):
                    pass  # ignora campos inválidos ou itens indisponíveis

        # Identifica se a ação de pagamento via cartão foi disparada
        pagar_cartao = 'pagar_cartao' in request.POST

        def reexibir(erro=None, erro_cvv=None, abrir_cartao=False):
            """Reexibe o formulário de pedido mantendo os dados e exibindo mensagens."""
            ctx = {
                'categorias':        self._carregar_categorias(),
                'formulario':        formulario,
                'form_cartao_salvo': form_cartao,
                'cartoes_usuario':   CartaoSalvo.objects.filter(usuario=request.user),
                'erro':              erro,
                'erro_cvv':          erro_cvv,
                'abrir_cartao':      abrir_cartao,
            }
            return render(request, 'cardapio/criarPedido.html', ctx)

        # Valida: pelo menos um item deve ser selecionado
        if not itens_pedido:
            return reexibir(erro='Selecione pelo menos um item com quantidade maior que zero.')

        # Valida o formulário de observações
        if not formulario.is_valid():
            return reexibir(abrir_cartao=pagar_cartao)

        # ── Pagamento via Cartão Salvo ────────────────────────────────────────
        if pagar_cartao:
            if not form_cartao.is_valid():
                return reexibir(abrir_cartao=True)

            cartao       = form_cartao.cleaned_data['cartao']
            cvv_digitado = form_cartao.cleaned_data['cvv']

            # Segurança: garante que o cartão pertence ao usuário logado
            if cartao.usuario != request.user:
                return reexibir(erro_cvv='Cartão inválido.', abrir_cartao=True)

            # Verifica se o CVV digitado corresponde ao CVV salvo no cartão
            if cartao.cvv != cvv_digitado:
                return reexibir(
                    erro_cvv='CVV incorreto. Verifique o código de segurança do cartão.',
                    abrir_cartao=True,
                )

            # Determina forma_pagamento conforme o tipo do cartão (crédito ou débito)
            forma = 'cartao_credito' if cartao.tipo == 'credito' else 'cartao_debito'

            pedido = Pedido.objects.create(
                cliente=request.user,
                status='recebido',
                observacoes=formulario.cleaned_data.get('observacoes') or '',
                forma_pagamento=forma,
                status_pagamento='pago',
                cartao_utilizado=cartao,
            )
            for item, quantidade in itens_pedido:
                ItemPedido.objects.create(pedido=pedido, item=item, quantidade=quantidade)

            total = sum(quantidade * item.preco for item, quantidade in itens_pedido)

            return render(request, 'cardapio/pagamentoConfirmado.html', {
                'pedido': pedido,
                'total':  total,
            })

        # Nenhum botão de pagamento reconhecido — reexibe o formulário com aviso
        return reexibir(
            erro='Selecione uma forma de pagamento para confirmar o pedido.',
        )


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

        # Filtro por status do pedido via query string (?status=VALOR)
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
            'pedidos':        pedidos,
            'status_choices': Pedido.STATUS_CHOICES,
            'status_filtro':  status_filtro,
            'data_filtro':    data_filtro or '',
        })


# ──────────────────────────────────────────────
# Cartões salvos do cliente
# ──────────────────────────────────────────────

class MeusCartoesView(LoginRequiredMixin, ClienteMixin, View):
    """
    Lista os cartões salvos do cliente logado (GET).
    Acesso: cliente. Template: meusCartoes.html.
    """

    def get(self, request):
        cartoes = request.user.cartoes.all()
        return render(request, 'cardapio/meusCartoes.html', {'cartoes': cartoes})


class AdicionarCartaoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe formulário para cadastrar novo cartão (GET).
    Valida, mascara o número e persiste o CartaoSalvo (POST).
    O número completo é descartado após extrair os últimos 4 dígitos —
    nunca é salvo no banco.
    Acesso: cliente. Template: adicionarCartao.html.
    """

    def get(self, request):
        return render(request, 'cardapio/adicionarCartao.html', {'formulario': CartaoForm()})

    def post(self, request):
        form = CartaoForm(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            numero = dados['numero_cartao']
            CartaoSalvo.objects.create(
                usuario=request.user,
                apelido=dados['apelido'],
                nome_titular=dados['nome_titular'],
                # Número completo descartado — apenas os últimos 4 dígitos são salvos
                numero_mascarado=f'**** **** **** {numero[-4:]}',
                bandeira=dados['bandeira'],
                tipo=dados['tipo'],
                validade=dados['validade'],
                cvv=dados['cvv'],
            )
            return redirect('cardapio:meus-cartoes')
        return render(request, 'cardapio/adicionarCartao.html', {'formulario': form})


class ExcluirCartaoView(LoginRequiredMixin, ClienteMixin, View):
    """
    Exibe confirmação antes de excluir o cartão (GET).
    Deleta o CartaoSalvo e redireciona (POST).
    A verificação usuario=request.user garante que o cliente
    só pode excluir seus próprios cartões.
    Acesso: cliente. Template: excluirCartao.html.
    """

    def _get_cartao(self, request, pk):
        # Garante que o cliente só acessa cartões próprios — outros retornam 404
        return get_object_or_404(CartaoSalvo, pk=pk, usuario=request.user)

    def get(self, request, pk):
        cartao = self._get_cartao(request, pk)
        return render(request, 'cardapio/excluirCartao.html', {'cartao': cartao})

    def post(self, request, pk):
        cartao = self._get_cartao(request, pk)
        cartao.delete()
        return redirect('cardapio:meus-cartoes')
