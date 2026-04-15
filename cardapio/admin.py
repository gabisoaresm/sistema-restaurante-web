# Registro dos modelos no painel administrativo do Django
from django.contrib import admin
from .models import Categoria, ItemCardapio, Pedido, ItemPedido, Perfil, CartaoSalvo

admin.site.register(Categoria)
admin.site.register(ItemCardapio)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Perfil)
admin.site.register(CartaoSalvo)
