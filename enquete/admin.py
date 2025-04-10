from django.contrib import admin
from .models import Enquete, Resposta


@admin.register(Enquete)
class EnqueteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'get_cargos', 'criado_formatado', 'atualizado_formatado', 'ativo')
    list_filter = ('ativo', 'created_dt', 'updated_dt', 'direcionado_a')
    search_fields = ('titulo', 'descricao')
    readonly_fields = ('created_dt', 'updated_dt')
    actions = ['excluir_enquetes']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'usuario', 'direcionado_a', 'ativo')  # Adicione 'usuario' aqui
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Opções de Resposta', {
            'fields': ('opcao1', 'opcao2', 'opcao3', 'opcao4')
        }),
        ('Informações do Sistema', {
            'fields': ('created_dt', 'updated_dt'),
            'classes': ('collapse',)
        }),
    )

    def get_cargos(self, obj):
        """Exibe os cargos direcionados à enquete"""
        return ", ".join(cargo.get_nome_display() for cargo in obj.direcionado_a.all())

    get_cargos.short_description = "Direcionado a"

    def criado_formatado(self, obj):
        """Formata a data de criação."""
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S") if obj.created_dt else "Data não disponível"
    criado_formatado.short_description = 'Criado em'
    criado_formatado.admin_order_field = 'created_dt'

    def atualizado_formatado(self, obj):
        """Formata a data de atualização."""
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S") if obj.updated_dt else "Data não disponível"
    atualizado_formatado.short_description = 'Atualizado em'
    atualizado_formatado.admin_order_field = 'updated_dt'

    def excluir_enquetes(self, request, queryset):
        """Permite excluir múltiplas enquetes selecionadas no admin."""
        total = queryset.count()
        queryset.delete()
        self.message_user(request, f"{total} enquetes foram excluídas com sucesso!", level="info")

    excluir_enquetes.short_description = "Excluir enquetes selecionadas"


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('enquete', 'get_usuario_cargo', 'resposta_resumida', 'get_data_resposta')
    list_filter = ('enquete',)
    search_fields = ('enquete__titulo', 'usuario__username', 'resposta', 'explicacao')  # Corrigido `membro` para `usuario`

    def get_usuario_cargo(self, obj):
        """Retorna o papel (role) do usuário que respondeu a enquete."""
        return obj.usuario.cargo if obj.usuario else "Sem usuário"
    get_usuario_cargo.short_description = 'Crargo na Recomeçar'

    def resposta_resumida(self, obj):
        """Exibe apenas os primeiros 50 caracteres da resposta para não poluir a interface."""
        return (obj.resposta[:50] + '...') if obj.resposta and len(obj.resposta) > 50 else obj.resposta
    resposta_resumida.short_description = 'Resposta'

    def get_data_resposta(self, obj):
        """Formata a data da resposta."""
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S") if obj.created_dt else "Data não disponível"
    get_data_resposta.short_description = 'Data da Resposta'
