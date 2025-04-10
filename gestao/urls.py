from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CursoView

app_name = 'gestao'


urlpatterns = [
    path('cursos', CursoView.as_view(), name='cursos'),


]
