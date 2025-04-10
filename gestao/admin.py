from django.contrib import admin
from .models import Pastores, Lideres, Cursos, Professores,\
    Celulas, Departamentos, Igrejas, Cultos, Colaboradores


@admin.register(Professores)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor',  'criado_formatado', 'atualizado_formatado', 'active_dt',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Cursos)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('valor', 'biografia', 'professor', 'inicio_curso', 'final_curso',
                    'criado_formatado', 'atualizado_formatado', 'active_dt')  # Remover 'fk_user' se for um campo de muitos-para-muitos

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'



@admin.register(Lideres)
class LiderAdmin(admin.ModelAdmin):
    list_display = ('nome_lider', 'email', 'whats', 'bio', 'criado_formatado', 'atualizado_formatado', 'active_dt',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Cultos)
class CultoAdmin(admin.ModelAdmin):
    list_display = ('culto', 'criado_formatado', 'atualizado_formatado', 'active_dt',)  # Alterado de 'mesa' para 'celula'

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Pastores)
class PastorAdmin(admin.ModelAdmin):
    list_display = ('pastor', 'igreja', 'cnpj', 'telefone', 'email', 'whats',
                    'facebook', 'instagram', 'linkedin', 'descricao',
                    'criado_formatado', 'atualizado_formatado',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Colaboradores)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'empresa', 'cnpj', 'whats', 'endereco', 'email', 'facebook',
                    'instagram', 'linkedin', 'preco_servico', 'desconto', 'criado_formatado',
                    'atualizado_formatado',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Celulas)
class CelulaAdmin(admin.ModelAdmin):
    list_display = ('celula_nome', 'fk_lider', 'negocio', 'whats', 'endereco', 'email', 'fk_user',  # Alterado de 'fk_associado' para 'fk_membro'
                    'participante', 'convidado', 'criado_formatado', 'atualizado_formatado', 'active_dt',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Departamentos)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('departamento', 'descricao', 'img', 'criado_formatado', 'atualizado_formatado', 'active_dt',)

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


@admin.register(Igrejas)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = (
        'nome_igreja', 'qrcode', 'link_cadastro', 'local', 'site',
        'whats', 'face', 'insta', 'linke', 'email', 'cnpj', 'logo',
        'criado_formatado', 'atualizado_formatado', 'active_dt',
        'menu1', 'menu2', 'menu3', 'menu4', 'menu5', 'menu6',
        'titulo1', 'descricao1', 'subtitulo1', 'subtitulo2',
        'titulo_link', 'titulo2', 'descricao2', 'img_fundo'
    )

    def criado_formatado(self, obj):
        return obj.created_dt.strftime("%d/%m/%Y %H:%M:%S")  # Formato: dia/mês/ano hora:minuto:segundo

    criado_formatado.short_description = 'Criado'

    def atualizado_formatado(self, obj):
        return obj.updated_dt.strftime("%d/%m/%Y %H:%M:%S")

    atualizado_formatado.short_description = 'Atualizado'


