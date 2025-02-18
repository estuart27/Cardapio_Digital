from django.shortcuts import redirect, reverse,render
from django.views.generic import ListView, DetailView
from django.views import View
# from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Pedido, ItemPedido
from produto.models import Variacao

from utils import utils


def painel(request):
    status = request.GET.get('status', 'todos')

    # Base queryset
    queryset = Pedido.objects.all().order_by('-data')

    # Filter by status if specified
    if status != 'todos':
        queryset = queryset.filter(status=status)

    context = {
        'pedidos': queryset,
        'status_choices': dict(Pedido._meta.get_field('status').choices)
    }

    return render(request, 'pedido/Painel.html', context)


@require_http_methods(["POST"])
def atualizar_status(request, pedido_id):
    try:
        pedido = Pedido.objects.get(pk=pedido_id)
        pedido.status = request.POST.get('status')
        pedido.save()
        return redirect(request.META.get('HTTP_REFERER', 'painel'))
    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido não encontrado')
        return redirect('painel')



class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedido = self.object
        context['pedido'] = pedido
        return context



#Com Estoque Removido da verificação
class SalvarPedido(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('perfil:criar')

        # if not self.request.session.get('carrinho'):
        #     messages.error(
        #         self.request,
        #         'Seu carrinho está vazio.'
        #     )
        #     return redirect('produto:lista')

        if not self.request.session.get('carrinho'):
            messages.success(
                self.request,
                'Pedido feito com Sucesso.'
            )
            return redirect('produto:lista')

        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]
        bd_variacoes = list(
            Variacao.objects.select_related('produto')
            .filter(id__in=carrinho_variacao_ids)
        )

        # Removida a verificação de estoque
        for variacao in bd_variacoes:
            vid = str(variacao.id)
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid].get('preco_unitario_promocional', 0)

            carrinho[vid]['preco_quantitativo'] = carrinho[vid]['quantidade'] * preco_unt
            carrinho[vid]['preco_quantitativo_promocional'] = carrinho[vid]['quantidade'] * preco_unt_promo

        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='Criado',
        )
        
        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                    observacao=v.get('observacao', ''),  # Use v.get para evitar KeyError
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['carrinho']

        return redirect(
            reverse(
                'pedido:pagar',
                kwargs={
                    'pk': pedido.pk
                }
            )
        )


class Detalhe(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'
    


class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'
    paginate_by = 10
    ordering = ['-id']










#observar carrinho e salvarpedido
# class SalvarPedido(View):
#     def get(self, *args, **kwargs):
#         if not self.request.user.is_authenticated:
#             messages.error(
#                 self.request,
#                 'Você precisa fazer login.'
#             )
#             return redirect('perfil:criar')

#         if not self.request.session.get('carrinho'):
#             messages.error(
#                 self.request,
#                 'Seu carrinho está vazio.'
#             )
#             return redirect('produto:lista')

#         carrinho = self.request.session.get('carrinho')
#         carrinho_variacao_ids = [v for v in carrinho]
#         bd_variacoes = list(
#             Variacao.objects.select_related('produto')
#             .filter(id__in=carrinho_variacao_ids)
#         )

#         for variacao in bd_variacoes:
#             vid = str(variacao.id)
#             estoque = variacao.estoque
#             qtd_carrinho = carrinho[vid]['quantidade']
#             preco_unt = carrinho[vid]['preco_unitario']
#             preco_unt_promo = carrinho[vid].get('preco_unitario_promocional', 0)

#             if estoque < qtd_carrinho:
#                 carrinho[vid]['quantidade'] = estoque
#                 carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
#                 carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unt_promo

#         qtd_total_carrinho = utils.cart_total_qtd(carrinho)
#         valor_total_carrinho = utils.cart_totals(carrinho)

#         pedido = Pedido(
#             usuario=self.request.user,
#             total=valor_total_carrinho,
#             qtd_total=qtd_total_carrinho,
#             status='Criado',
#         )
#         pedido.save()

#         ItemPedido.objects.bulk_create(
#             [
#                 ItemPedido(
#                     pedido=pedido,
#                     produto=v['produto_nome'],
#                     produto_id=v['produto_id'],
#                     variacao=v['variacao_nome'],
#                     variacao_id=v['variacao_id'],
#                     preco=v['preco_quantitativo'],
#                     preco_promocional=v['preco_quantitativo_promocional'],
#                     quantidade=v['quantidade'],
#                     imagem=v['imagem'],
#                     observacao=v.get('observacao', ''),  # Use v.get para evitar KeyError
#                 ) for v in carrinho.values()
#             ]
#         )

#         del self.request.session['carrinho']

#         return redirect(
#             reverse(
#                 'pedido:pagar',
#                 kwargs={
#                     'pk': pedido.pk
#                 }
#             )
#         )