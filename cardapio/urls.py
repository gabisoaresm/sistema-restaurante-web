# =============================================================================
# urls.py — Rotas do app cardapio.
#
# Todas as rotas usam o namespace 'cardapio', definido por app_name.
# Isso permite referenciar URLs nos templates com {% url 'cardapio:nome' %}.
# As rotas de autenticação (login, logout, registro) ficam no urls.py do projeto.
# =============================================================================

from django.urls import path
from .views import (
    HomeView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    ItemCardapioListView, ItemCardapioCreateView, ItemCardapioUpdateView, ItemCardapioDeleteView,
    CriarPedidoView, MeusPedidosView,
    FilaPedidosView, AtualizarStatusPedidoView, PainelGerenteView,
    PerfilView,
    GerenciarUsuariosView, AlterarPerfilUsuarioView,
)

# Namespace do app — obrigatório para {% url 'cardapio:...' %} funcionar
app_name = 'cardapio'

urlpatterns = [

    # ── Página inicial ────────────────────────────────────────────────────────
    path('', HomeView.as_view(), name='home'),

    # ── CRUD de Categoria (só gerente) ───────────────────────────────────────
    path('categorias/', CategoriaListView.as_view(), name='lista-categorias'),
    path('categorias/nova/', CategoriaCreateView.as_view(), name='cria-categoria'),
    path('categorias/editar/<int:pk>/', CategoriaUpdateView.as_view(), name='atualiza-categoria'),
    path('categorias/excluir/<int:pk>/', CategoriaDeleteView.as_view(), name='apaga-categoria'),

    # ── CRUD de ItemCardapio (lista: logado; criar/editar/excluir: gerente) ───
    path('itens/', ItemCardapioListView.as_view(), name='lista-itens'),
    path('itens/novo/', ItemCardapioCreateView.as_view(), name='cria-item'),
    path('itens/editar/<int:pk>/', ItemCardapioUpdateView.as_view(), name='atualiza-item'),
    path('itens/excluir/<int:pk>/', ItemCardapioDeleteView.as_view(), name='apaga-item'),

    # ── Perfil do usuário ─────────────────────────────────────────────────────
    path('perfil/', PerfilView.as_view(), name='perfil'),

    # ── Gerenciamento de usuários (só gerente) ────────────────────────────────
    path('usuarios/', GerenciarUsuariosView.as_view(), name='gerenciar-usuarios'),
    path('usuarios/alterar/<int:pk>/', AlterarPerfilUsuarioView.as_view(), name='alterar-perfil-usuario'),

    # ── Pedidos do cliente ────────────────────────────────────────────────────
    path('pedidos/novo/', CriarPedidoView.as_view(), name='criar-pedido'),
    path('pedidos/meus/', MeusPedidosView.as_view(), name='meus-pedidos'),

    # ── Fila e gestão de pedidos (atendente e gerente) ───────────────────────
    path('pedidos/fila/', FilaPedidosView.as_view(), name='fila-pedidos'),
    path('pedidos/status/<int:pk>/', AtualizarStatusPedidoView.as_view(), name='atualizar-status'),
    path('pedidos/painel/', PainelGerenteView.as_view(), name='painel-gerente'),
]
