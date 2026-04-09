# URLs do app cardapio
from django.urls import path
from .views import HomeView, CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView

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
]
