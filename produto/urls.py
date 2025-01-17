from django.urls import path
from . import views


app_name = 'produto'

urlpatterns = [
    path('', views.ListaProdutos.as_view(), name="lista"),
    path('produto/<slug:slug>/', views.DetalheProduto.as_view(), name="detalhe"),
    path('adicionaraocarrinho/', views.AdicionarAoCarrinho.as_view(),
         name="adicionaraocarrinho"),
    path('removerdocarrinho/', views.RemoverDoCarrinho.as_view(),
         name="removerdocarrinho"),
    path('carrinho/', views.Carrinho.as_view(), name="carrinho"),
    path('resumodacompra/', views.ResumoDaCompra.as_view(), name="resumodacompra"),
    path('busca/', views.Busca.as_view(), name="busca"),
    path('inicial', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('layout-static/', views.layout_static, name='layout_static'),
    path('layout-sidenav-light/', views.layout_sidenav_light, name='layout_sidenav_light'),
    path('register/', views.register, name='register'),
    path('password/', views.password, name='password'),
    path('charts/', views.charts, name='charts'),
    path('tables/', views.tables, name='tables'),         
    path('adicionar/',views.pagina_adicionar, name='adicionar'),
]