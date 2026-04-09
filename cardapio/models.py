# Modelos do sistema de pedidos do restaurante
from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    """Categoria dos itens do cardápio (ex: Entradas, Pratos Principais, Bebidas)."""
    nome = models.CharField(max_length=100, help_text='Nome da categoria')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class ItemCardapio(models.Model):
    """Item disponível no cardápio do restaurante."""
    nome = models.CharField(max_length=200, help_text='Nome do item')
    descricao = models.TextField(help_text='Descrição do item')
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Preço do item em reais'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        help_text='Categoria à qual este item pertence'
    )
    disponivel = models.BooleanField(
        default=True,
        help_text='Indica se o item está disponível para pedido'
    )

    class Meta:
        ordering = ['categoria', 'nome']
        verbose_name = 'Item do Cardápio'
        verbose_name_plural = 'Itens do Cardápio'

    def __str__(self):
        return f'{self.nome} ({self.categoria})'


class Pedido(models.Model):
    """Pedido realizado por um cliente."""

    # Opções de status do pedido
    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('em_preparo', 'Em Preparo'),
        ('pronto', 'Pronto'),
        ('entregue', 'Entregue'),
    ]

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Cliente que realizou o pedido'
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        help_text='Data e hora em que o pedido foi realizado'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='recebido',
        help_text='Status atual do pedido'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text='Observações adicionais do cliente sobre o pedido'
    )

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.pk} — {self.cliente} ({self.get_status_display()})'


class ItemPedido(models.Model):
    """Item individual dentro de um pedido."""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        help_text='Pedido ao qual este item pertence'
    )
    item = models.ForeignKey(
        ItemCardapio,
        on_delete=models.CASCADE,
        help_text='Item do cardápio selecionado'
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        help_text='Quantidade do item no pedido'
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.item} no Pedido #{self.pedido.pk}'


class Perfil(models.Model):
    """Perfil estendido do usuário com o tipo de acesso no sistema."""

    # Tipos de usuário do sistema
    TIPO_CHOICES = [
        ('gerente', 'Gerente'),
        ('atendente', 'Atendente'),
        ('cliente', 'Cliente'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text='Usuário do Django associado a este perfil'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='cliente',
        help_text='Tipo de acesso do usuário no sistema'
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_tipo_display()})'
