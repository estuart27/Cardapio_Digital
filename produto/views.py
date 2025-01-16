from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
import json
from django.db.models import Q
from . import models
from perfil.models import Perfil
from .models import Category,Produto
from django.shortcuts import render
from pedido.models import Pedido, ItemPedido  # Importa os modelos de Pedido e ItemPedido



def index(request):
    return render(
        request,
        'produto/index.html',
    )

def login(request):
    return render(
        request,
        'produto/login.html',
    )
def layout_static(request):
    return render(
        request,
        'produto/layout-static.html',
    )

def layout_sidenav_light(request):
    return render(
        request,
        'produto/layout-sidenav-light.html',
    )

def register(request):
    return render(
        request,
        'produto/register.html',
    )

def password(request):
    return render(
        request,
        'produto/password.html',
    )

def charts(request):
    return render(
        request,
        'produto/charts.html',
    )



def tables(request):
    pedidos = Pedido.objects.prefetch_related('itempedido_set').all()  # Obtém todos os pedidos com os itens relacionados
    return render(
        request,
        'produto/tables.html',
        {
            'pedidos': pedidos  # Passa os pedidos para o contexto do template
        },
    )



class ListaProdutos(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['is_lista_page'] = True  # Adiciona uma variável para identificar a página
        return context


class Busca(ListaProdutos):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs

        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )

        self.request.session.save()
        return qs


class DetalheProduto(DetailView):
    model = Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto = self.get_object()
        
        

        if produto.category:
            context['produtos_relacionados'] = Produto.objects.filter(
                category=produto.category
            ).exclude(id=produto.id).order_by('-id')[:4]  # Ordena os mais recentes
        else:
            context['produtos_relacionados'] = Produto.objects.all().exclude(
                id=produto.id
            ).order_by('-id')[:4]  # Ordena por produtos mais recentes

        return context


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get('HTTP_REFERER', reverse('produto:lista'))
        variacao_id = self.request.GET.get('vid')
        quantidade = int(self.request.GET.get('quantidade', 1))  # Pega a quantidade
        try:
            observacao = self.request.GET['observacao']  # Acessa diretamente
        except KeyError:
            observacao = ''
        print("O parâmetro 'observacao' não foi encontrado na requisição.")

        if not variacao_id:
            messages.error(self.request, 'Produto não existe')
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        slug = produto.slug
        imagem = produto.imagem.name if produto.imagem else ''

        # Garante que o carrinho seja um dicionário
        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
        carrinho = self.request.session['carrinho']

        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except json.JSONDecodeError:
                carrinho = {}

        # Adiciona ou atualiza o produto no carrinho
        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += quantidade  # Adiciona a nova quantidade
            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario * quantidade,  # Multiplica pela quantidade
                'preco_quantitativo_promocional': preco_unitario_promocional * quantidade,
                'quantidade': quantidade,
                'slug': slug,
                'imagem': imagem,
                'observacao': observacao,  
            }

        # Salva o carrinho na sessão como um dicionário
        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        # Armazenar o item no modelo ItemPedido
        pedido = Pedido.objects.first()  # Ajuste para obter a instância de Pedido correta
        if pedido:
            item_pedido = ItemPedido(
                pedido=pedido,
                produto=produto_nome,
                produto_id=produto_id,
                variacao=variacao_nome,
                variacao_id=variacao_id,
                preco=preco_unitario,
                preco_promocional=preco_unitario_promocional,
                quantidade=quantidade,
                imagem=imagem,
                observacao=observacao,  # Salva a observação
            )
            item_pedido.save()

        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu '
            f'carrinho {carrinho[variacao_id]["quantidade"]}x.'
        )

        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session['carrinho']:
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]

        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} '
            f'removido do seu carrinho.'
        )

        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)



class Carrinho(View):
    def get(self, *args, **kwargs):
        carrinho = self.request.session.get('carrinho', {})

        # Converte para dicionário se necessário
        if isinstance(carrinho, str):
            try:
                carrinho = json.loads(carrinho)
            except json.JSONDecodeError:
                carrinho = {}

        contexto = {
            'carrinho': carrinho
        }

        return render(self.request, 'produto/carrinho.html', contexto)




class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Usuário sem perfil.'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio.'
            )
            return redirect('produto:lista')

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }

        return render(self.request, 'produto/resumodacompra.html', contexto)