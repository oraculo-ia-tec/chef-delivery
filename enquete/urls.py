# oraculo/urls.py

from django.urls import path
from .views import criar_enquete, verificar_resposta, CustomAuthToken

urlpatterns = [

    path('criar_enquete/', criar_enquete, name='criar_enquete'),
    path('verificar_resposta/<int:enquete_id>/', verificar_resposta, name='verificar_resposta'),
    path('api/token/', CustomAuthToken.as_view(), name='api_token_auth'),

]