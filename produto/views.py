from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from . import models
from perfil.models import Perfil
from .models import Category,Produto,Variacao
from django.shortcuts import render
from pedido.models import Pedido, ItemPedido  # Importa os modelos de Pedido e ItemPedido]
from django.core.paginator import Paginator
from .forms import ProdutoForm  # Certifique-se de ter um formulário configurado
from django.db import transaction
import json



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
    clientes = Perfil.objects.all()
    total_clientes = clientes.count()
    
    context = {
        'clientes': clientes,
        'total_clientes': total_clientes,
    }
    return render(request, 'produto/layout-static.html', context)


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


def layout_sidenav_light(request):
    produtos = Produto.objects.all()  # Obtenha todos os produtos para enviar ao template

    if request.method == 'POST':
        if 'delete' in request.POST:
            produto_id = request.POST.get('produto_id')
            produto = get_object_or_404(Produto, id=produto_id)
            produto.delete()
            messages.success(request, 'Produto excluído com sucesso!')

        if 'toggle_visibility' in request.POST:
            produto_id = request.POST.get('produto_id')
            produto = get_object_or_404(Produto, id=produto_id)
            produto.visivel = not produto.visivel
            produto.save()
            messages.success(request, 'Visibilidade do produto alterada com sucesso!')

    # Pegando todas as categorias
    categories = Category.objects.all()
    
    # Filtrando produtos por categoria
    category_id = request.GET.get('category')
    if category_id:
        produtos_list = Produto.objects.filter(category_id=category_id)
    else:
        produtos_list = Produto.objects.all()

    # Configuração do paginador
    page = request.GET.get('page', 1)
    paginator = Paginator(produtos_list, 10)  # 10 produtos por página
    try:
        produtos = paginator.page(page)
    except:
        produtos = paginator.page(1)

    return render(
        request,
        'produto/layout-sidenav-light.html',
        {
            'produtos': produtos,
            'categories': categories,
            'selected_category': category_id
        }
    )



def editar_produto_modal(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Produto atualizado com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'html': render_to_string('produto/editar_produto_form.html', 
                                       {'form': form}, 
                                       request=request)
            })
    else:
        form = ProdutoForm(instance=produto)
        return JsonResponse({
            'success': True,
            'html': render_to_string('produto/editar_produto_form.html', 
                                   {'form': form}, 
                                   request=request)
        })


def pagina_adicionar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Salva o produto
                    produto = form.save()
                    
                    # Processa as variações
                    variacoes_nome = request.POST.getlist('variacoes_nome[]')
                    variacoes_preco = request.POST.getlist('variacoes_preco[]')
                    variacoes_preco_promocional = request.POST.getlist('variacoes_preco_promocional[]')
                    variacoes_estoque = request.POST.getlist('variacoes_estoque[]')

                    # Cria as variações se for produto variável
                    if produto.tipo == 'V':
                        for i in range(len(variacoes_nome)):
                            if variacoes_nome[i].strip():  # Verifica se o nome não está vazio
                                Variacao.objects.create(
                                    produto=produto,
                                    nome=variacoes_nome[i],
                                    preco=float(variacoes_preco[i] or 0),
                                    preco_promocional=float(variacoes_preco_promocional[i] or 0),
                                    estoque=int(variacoes_estoque[i] or 0)
                                )

                messages.success(request, 'Produto salvo com sucesso!')
                return redirect('produto:index')

            except Exception as e:
                messages.error(request, f'Erro ao salvar produto: {str(e)}')
    else:
        form = ProdutoForm()

    context = {
        'form': form,
        'categories': Category.objects.all()
    }
    return render(request, 'produto/adicionar.html', context)


# Pagina de adminstração de produtos -----------------------------------------


from django.views.generic import ListView
from .models import Produto, Category  # Certifique-se de que o modelo Category está importado

class ListaProdutos(ListView):
    model = Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 17
    ordering = ['-id']

    def get_queryset(self):
        # Filtra apenas produtos visíveis
        queryset = Produto.objects.filter(visivel=True)

        # Filtra por categoria, se aplicável
        category_id = self.request.GET.get('category')
        if category_id == 'all':
            # Retorna todos os produtos se a categoria for 'all'
            return queryset
        elif category_id:
            # Filtra produtos pela categoria se uma categoria específica for fornecida
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.order_by(*self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Todas as categorias
        context['is_lista_page'] = True  # Identificador da página
        context['selected_category'] = self.request.GET.get('category')  # Categoria selecionada
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