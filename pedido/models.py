from django.db import models
from django.contrib.auth.models import User


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField()
    qtd_total = models.PositiveIntegerField()
    status = models.CharField(
        default="Criado",
        max_length=10,
        choices=(
            ('Criado', 'Criado'),
            ('Pendente', 'Pendente'),
            ('Enviado', 'Enviado'),
            ('Finalizado', 'Finalizado'),
        )
    )
    data = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True)

    @property
    def timestamp(self):
        return self.data.isoformat()

    def __str__(self):
        return f'Pedido N. {self.pk}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    produto = models.CharField(max_length=255)
    produto_id = models.PositiveIntegerField()
    variacao = models.CharField(max_length=255)
    variacao_id = models.PositiveIntegerField()
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    quantidade = models.PositiveIntegerField()
    imagem = models.CharField(max_length=2000)
    observacao = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'Item do {self.pedido}'

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'