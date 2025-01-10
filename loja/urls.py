from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Certifique-se que o admin está no topo para evitar conflitos
    path('', include('produto.urls')),  # Rotas para produtos
    path('perfil/', include('perfil.urls')),  # Rotas para perfil
    path('pedido/', include('pedido.urls')),  # Rotas para pedido
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Configuração de arquivos de mídia
