
from django.urls import path
from .views import criar_usuario


urlpatterns = [
    path('criar_usuario/', criar_usuario, name='criar_usuario'),


]