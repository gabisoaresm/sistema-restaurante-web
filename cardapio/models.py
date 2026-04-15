# =============================================================================
# models.py — Modelos de dados do sistema de pedidos do restaurante.
#
# Estrutura de relacionamentos:
#   Categoria ──< ItemCardapio     (uma categoria tem muitos itens)
#   User ──< Pedido                (um usuário faz vários pedidos)
#   Pedido ──< ItemPedido >── ItemCardapio  (pedido tem vários itens do cardápio)
#   User ──1 Perfil                (cada usuário tem um perfil: gerente/atendente/cliente)
#   User ──< CartaoSalvo           (um cliente pode ter vários cartões salvos)
#   Pedido >── CartaoSalvo         (pedido pode referenciar o cartão utilizado)
# =============================================================================

from django.db import models
from django.contrib.auth.models import User


# ── Cardápio ─────────────────────────────────────────────────────────────────

class Categoria(models.Model):
    """
    Categoria dos itens do cardápio (ex: Entradas, Pratos Principais, Bebidas).
    Usada para agrupar e filtrar os itens na listagem do cardápio.
    """
    nome = models.CharField(max_length=100, help_text='Nome da categoria')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class ItemCardapio(models.Model):
    """
    Item disponível no cardápio do restaurante.
    Pertence a uma Categoria e pode ser marcado como indisponível
    sem precisar ser removido do banco.
    """
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


# ── Cartões salvos ────────────────────────────────────────────────────────────

class CartaoSalvo(models.Model):
    """
    Cartão de pagamento salvo pelo cliente para uso em pedidos futuros.
    IMPORTANTE: o número completo do cartão NUNCA é salvo no banco —
    apenas os últimos 4 dígitos (numero_mascarado).
    O CVV é salvo para permitir validação no momento do pagamento simulado.
    """

    BANDEIRA_CHOICES = [
        ('visa',       'Visa'),
        ('mastercard', 'Mastercard'),
        ('elo',        'Elo'),
        ('amex',       'American Express'),
    ]
    TIPO_CHOICES = [
        ('credito', 'Crédito'),
        ('debito',  'Débito'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cartoes',
        help_text='Cliente dono do cartão',
    )
    apelido = models.CharField(
        max_length=50,
        help_text='Ex: Nubank, Visa final 1234',
    )
    nome_titular = models.CharField(max_length=200)
    # Apenas os últimos 4 dígitos são salvos — número completo nunca é persistido
    numero_mascarado = models.CharField(
        max_length=19,
        help_text='Ex: **** **** **** 1234',
    )
    bandeira = models.CharField(max_length=20, choices=BANDEIRA_CHOICES)
    tipo     = models.CharField(max_length=10, choices=TIPO_CHOICES)
    validade = models.CharField(max_length=7, help_text='MM/AAAA')
    # CVV salvo para validação posterior no momento do pagamento
    cvv = models.CharField(max_length=4, help_text='Código de segurança do cartão')

    def __str__(self):
        return f'{self.apelido} ({self.numero_mascarado})'

    class Meta:
        ordering = ['apelido']
        verbose_name = 'Cartão Salvo'
        verbose_name_plural = 'Cartões Salvos'


# ── Pedidos ───────────────────────────────────────────────────────────────────

class Pedido(models.Model):
    """
    Pedido realizado por um cliente.
    Agrupa um ou mais ItemPedido e acompanha o ciclo de vida
    do pedido pelo campo status.
    """

    # Ciclo de vida do pedido: recebido → em_preparo → pronto → entregue
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

    # ── Pagamento ─────────────────────────────────────────────────────────────

    FORMA_PAGAMENTO_CHOICES = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito',  'Cartão de Débito'),
        ('pix',            'PIX'),
    ]
    STATUS_PAGAMENTO_CHOICES = [
        ('pendente',  'Pendente'),
        ('pago',      'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        blank=True,
        help_text='Forma de pagamento escolhida pelo cliente',
    )
    status_pagamento = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO_CHOICES,
        default='pendente',
        help_text='Estado atual do pagamento',
    )
    cartao_utilizado = models.ForeignKey(
        'CartaoSalvo',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Cartão salvo usado neste pedido (se aplicável)',
    )

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.pk} — {self.cliente} ({self.get_status_display()})'


class ItemPedido(models.Model):
    """
    Item individual dentro de um pedido.
    Liga um Pedido a um ItemCardapio com a quantidade solicitada.
    Acesso reverso a partir do Pedido: pedido.itens.all()
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',       # pedido.itens.all() nos templates/views
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


# ── Perfil de usuário ─────────────────────────────────────────────────────────

class Perfil(models.Model):
    """
    Perfil estendido do usuário com o tipo de acesso no sistema.
    Relação OneToOne com User — criado no momento do registro.
    O tipo define quais views e funcionalidades o usuário pode acessar:
      - gerente: CRUD completo e painel de pedidos
      - atendente: fila de pedidos e atualização de status
      - cliente: fazer pedidos e consultar os próprios pedidos
    """

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
