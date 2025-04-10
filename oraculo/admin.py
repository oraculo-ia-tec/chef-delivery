
from django.contrib import admin
from .models import User
from .models import Cargo


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome',)  # Campos a serem exibidos na lista
    search_fields = ('nome',)  # Permite pesquisa pelo nome
    ordering = ('nome',)       # Ordena a lista pelo nome


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpf_cnpj', 'email', 'whatsapp', 'cargo')  # Substituí `role` por `cargo`
    search_fields = ('name', 'email', 'username')
    list_filter = ('cargo',)  # Substituí `role` por `cargo`






