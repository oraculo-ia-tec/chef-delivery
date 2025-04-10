"""
URL configuration for oraculo-biblia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from gestao.views import IndexView, AcessaView, CadastroView, DashboardView,EmpresasView, QuemSomosView, \
    EventoView, NetworkView


urlpatterns = [
    path('painel-oraculo/', admin.site.urls),
    path('', IndexView.as_view(), name='home'),
    path('', include('gestao.urls', namespace='curso')),
    path('oraculo/api/', include('oraculo.urls')),
    path('enquete/', include('enquete.urls')),
    path('acessa/', AcessaView.as_view(), name='acessa'),
    path('registrar/', CadastroView.as_view(), name='registrar'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('catalogo-digital/', EmpresasView.as_view(), name='catalogo-digital'),
    path('quem-somos/', QuemSomosView.as_view(), name='quem-somos'),
    path('network-mentorias/', NetworkView.as_view(), name='network-mentorias'),
    path('eventos/', EventoView.as_view(), name='eventos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
