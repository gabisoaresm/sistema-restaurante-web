# URLs do app cardapio
from django.urls import path
from .views import (
    HomeView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    ItemCardapioListView, ItemCardapioCreateView, ItemCardapioUpdateView, ItemCardapioDeleteView,
    CriarPedidoView, MeusPedidosView,
    FilaPedidosView, AtualizarStatusPedidoView, PainelGerenteView,
)

# Namespace do app — permite usar {% url 'cardapio:nome-da-rota' %} nos templates
app_name = 'cardapio'

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),

    # CRUD de Categoria
    path('categorias/', CategoriaListView.as_view(), name='lista-categorias'),
    path('categorias/nova/', CategoriaCreateView.as_view(), name='cria-categoria'),
    path('categorias/editar/<int:pk>/', CategoriaUpdateView.as_view(), name='atualiza-categoria'),
    path('categorias/excluir/<int:pk>/', CategoriaDeleteView.as_view(), name='apaga-categoria'),

    # CRUD de ItemCardapio
    path('itens/', ItemCardapioListView.as_view(), name='lista-itens'),
    path('itens/novo/', ItemCardapioCreateView.as_view(), name='cria-item'),
    path('itens/editar/<int:pk>/', ItemCardapioUpdateView.as_view(), name='atualiza-item'),
    path('itens/excluir/<int:pk>/', ItemCardapioDeleteView.as_view(), name='apaga-item'),

    # Pedidos do cliente
    path('pedidos/novo/', CriarPedidoView.as_view(), name='criar-pedido'),
    path('pedidos/meus/', MeusPedidosView.as_view(), name='meus-pedidos'),

    # Fila e gestão de pedidos (atendente/gerente)
    path('pedidos/fila/', FilaPedidosView.as_view(), name='fila-pedidos'),
    path('pedidos/status/<int:pk>/', AtualizarStatusPedidoView.as_view(), name='atualizar-status'),
    path('pedidos/painel/', PainelGerenteView.as_view(), name='painel-gerente'),
]
