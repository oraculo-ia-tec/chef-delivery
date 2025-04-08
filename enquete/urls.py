# oraculo/urls.py

from django.urls import path
from .views import criar_usuario, criar_novo_membro, teste_oraculo, enquete_igreja, resposta_enquete

urlpatterns = [
    path('api/criar_usuario/', criar_usuario, name='criar_usuario'),
    path('api/criar_novo_membro/', criar_novo_membro, name='criar_novo_membro'),
    path('api/teste_oraculo/', teste_oraculo, name='teste_oraculo'),
    path('api/enquete_igreja/', enquete_igreja, name='enquete_igreja'),
    path('api/resposta_enquete/', resposta_enquete, name='resposta_enquete'),
]