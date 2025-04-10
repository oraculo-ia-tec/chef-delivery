from django.db import models
from django.utils import timezone
from stdimage.models import StdImageField
from .slug_url import generate_slug
from oraculo.models import Cargo, User


class Base(models.Model):
    created_dt = models.DateTimeField('Criado',default=timezone.now)
    updated_dt = models.DateTimeField('Atualizado',default=timezone.now)
    active_dt = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True


class Professores(Base):

    professor = models.CharField('Professor', max_length=100)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

    def __str__(self):
        return self.professor


class Cultos(Base):
    culto = models.CharField('Nome', max_length=100)

    class Meta:
        verbose_name = 'Culto'
        verbose_name_plural = 'Cultos'

    def __str__(self):
        return self.culto


class Departamentos(Base):
    departamento = models.CharField('Nome', max_length=100)
    descricao = models.TextField(max_length=150)
    img = StdImageField('Imagem', upload_to='Departamentos', variations={'thumb': {'width': 100, 'height': 100, 'crop': True}}, null=True, default=None)

    class Meta:
        verbose_name = 'departamento'
        verbose_name_plural = 'Departamentos'

    @classmethod
    def contador_Departamentos(cls):
        """Retorna o número total de departamentos cadastrados."""
        try:
            return cls.objects.count()
        except Exception as e:
            # Log ou tratar a exceção conforme necessário
            print(f"Erro ao contar departamentos: {str(e)}")
            return 0

    def __str__(self):
        return self.departamento


class Pastores(Base):
    pastor = models.CharField(max_length=100)  # Altera 'colaborador' para 'pastor'
    igreja = models.CharField('IGREJA', max_length=100)  # Campo para nome da igreja
    departamento = models.ForeignKey(Departamentos, on_delete=models.CASCADE)
    cnpj = models.CharField('CNPJ', max_length=20, null=True, blank=True)  # CNPJ pode não ser obrigatório para pastores
    endereco = models.CharField(max_length=200)
    telefone = models.CharField('Telefone', max_length=15, null=True, blank=True)  # Campo para telefone
    email = models.EmailField('E-MAIL', max_length=100)
    whats = models.CharField('WhatsApp', max_length=11, default='#')
    facebook = models.CharField('Facebook', max_length=100, default='#')
    instagram = models.CharField('Instagram', max_length=100, default='#')
    linkedin = models.CharField('Linkedin', max_length=100, default='#')
    foto = StdImageField(upload_to='fotos_pastores', variations={'thumb':
         {'width':500,'height':500,'crop':True }}, null=True, default=None)  # Campo para foto do pastor
    descricao = models.TextField(max_length=300, default='#')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = generate_slug(self, 'pastor')  # Altera 'colaborador' para 'pastor'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Pastor'  # Altera para 'Pastor'
        verbose_name_plural = 'Pastores'  # Altera para 'Pastores'

    def __str__(self):
        return self.pastor  # Altera para 'pastor'


class Lideres(Base):
    nome_lider = models.CharField(max_length=100)
    email = models.EmailField('E-mail', max_length=100, default='#')
    whats = models.IntegerField('WhatsApp', default=0, null=False)
    professor = models.ForeignKey(Professores, on_delete=models.SET_NULL, null=True)
    bio = models.TextField('Biografia', max_length=150)
    facebook = models.CharField('Facebook', max_length=100, default='#')
    instagram = models.CharField('Instagram', max_length=100, default='#')
    linkedin = models.CharField('Linkedin', max_length=100, default='#')
    perfil = StdImageField('Perfil',upload_to='perfil_lider',variations={'thumb':
         {'width':100,'height':100,'crop':True }},null=True, default=None)

    class Meta:
        verbose_name = 'Lider'
        verbose_name_plural = 'Lideres'

    def __str__(self):
        return self.nome_lider


class Mentorias(Base):

    mentoria = models.CharField('Mentoria', max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(max_length=100)
    n_lider = models.ForeignKey(Lideres, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Mentoria'
        verbose_name_plural = 'Mentorias'

    def get_formatted_preco(self):
        return 'R$ {:.2f}'.format(self.preco)

    def __str__(self):
        return self.mentoria


class Eventos(models.Model):
    nome_evento = models.CharField(max_length=100)
    palestrante = models.CharField(max_length=100)
    tema_evento = models.CharField(max_length=100, default='#')
    bio = models.TextField(max_length=300)
    local = models.CharField(max_length=100)
    email = models.EmailField('E-MAIL', max_length=100)
    whats = models.CharField('WhatsApp', max_length=20, default='#')  # Aumentado para suportar números completos
    face = models.CharField('Facebook', max_length=100, default='#')
    insta = models.CharField('Instagram', max_length=100, default='#')
    linke = models.CharField('Linkedin', max_length=100, default='#')
    dia_evento = models.DateTimeField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    img = models.ImageField(upload_to='img_palestrante', null=True, default=None)

    # 📌 Relacionamento ManyToMany para direcionar o evento a cargos específicos
    direcionado_a = models.ManyToManyField(Cargo, through="EventoCargo", related_name="eventos")

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.nome_evento


class EventoCargo(models.Model):
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('evento', 'cargo')  # Evita duplicação


class Colaboradores(Base):
    colaborador = models.CharField(max_length=100)  # Altera 'membro' para 'colaborador'
    empresa = models.CharField('EMPRESA', max_length=100)
    departamento = models.ForeignKey(Departamentos, on_delete=models.CASCADE)
    cnpj = models.CharField('CNPJ', max_length=20)
    endereco = models.CharField(max_length=200)
    preco_servico = models.DecimalField(max_digits=8, decimal_places=2)
    desconto = models.IntegerField()
    email = models.EmailField('E-MAIL', max_length=100)
    whats = models.CharField('WhatsApp', max_length=11, default='#')
    facebook = models.CharField('Facebook', max_length=100, default='#')
    instagram = models.CharField('Instagram', max_length=100, default='#')
    linkedin = models.CharField('Linkedin', max_length=100, default='#')
    logo = StdImageField(upload_to='logomarca', variations={'thumb':
         {'width':500,'height':500,'crop':True }}, null=True, default=None)
    descricao = models.TextField(max_length=300, default='#')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = generate_slug(self, 'colaborador')  # Altera 'membro' para 'colaborador'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Colaborador'  # Altera para 'Colaborador'
        verbose_name_plural = 'Colaboradores'  # Altera para 'Colaboradores'

    def __str__(self):
        return self.colaborador  # Altera para 'colaborador'


class Celulas(Base):
    celula_nome = models.CharField(max_length=100)
    fk_lider = models.ForeignKey(Lideres,max_length=100, on_delete=models.CASCADE)
    negocio = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    fk_user = models.ForeignKey(User,max_length=100, on_delete=models.CASCADE)
    email = models.EmailField('E-MAIL', max_length=100)
    whats = models.CharField('WhatsApp', max_length=11, default='#')
    participante = models.CharField(max_length=100)
    convidado = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Celula'
        verbose_name_plural = 'Celulas'

    def __str__(self):
        return self.Celula_nome


class Cursos(Base):

    curso = models.CharField( max_length=100)
    professor = models.ForeignKey(Professores, max_length=100, on_delete=models.CASCADE)
    biografia = models.TextField('Bio', max_length=250)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    fk_user = models.ManyToManyField(User)
    inicio_curso = models.DateTimeField()
    final_curso = models.DateTimeField()

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.curso


class Igrejas(Base):
    nome_igreja = models.CharField('Nome da Igreja', max_length=150, default='#')
    menu1 = models.CharField('Menu1', max_length=10, default='#')
    menu2 = models.CharField('Menu2', max_length=10, default='#')
    menu3 = models.CharField('Menu3', max_length=10, default='#')
    menu4 = models.CharField('Menu4', max_length=10, default='#')
    menu5 = models.CharField('Menu5', max_length=10, default='#')
    menu6 = models.CharField('Menu6', max_length=10, default='#')
    titulo1 = models.CharField('Título1', max_length=15, default='#')
    descricao1 = models.TextField('Descrição1', max_length=100, default='#')
    subtitulo1 = models.CharField('Subtitulo1', max_length=10, default='#')
    subtitulo2 = models.CharField('Subtitulo2', max_length=10, default='#')
    titulo_link = models.CharField('Título com Link', max_length=200, default='#')
    img_fundo= StdImageField('Imagem de Fundo1',upload_to='img_fundo',variations={'thumb':
         {'width':1920,'height':1200,'crop':True }},null=True, default=None)
    titulo2 = models.CharField('Título2', max_length=15, default='#')
    descricao2 = models.TextField('Descrição2', max_length=300, default='#')
    qrcode = StdImageField('QRCODE',upload_to='qrcode',variations={'thumb':
         {'width':600,'height':600,'crop':True }},null=True, default=None)
    link_cadastro = models.CharField('Link de cadatro:', max_length=200, default='#')
    local = models.CharField(max_length=100, default='#')
    site = models.CharField(max_length=100, default='#')
    whats = models.CharField('WhatsApp', max_length=11, default='#')
    face = models.CharField('Facebook', max_length=100, default='#')
    insta = models.CharField('Instagram', max_length=100, default='#')
    linke = models.CharField('Linkedin', max_length=100, default='#')
    email = models.EmailField('E-MAIL', max_length=100)
    cnpj = models.CharField(max_length=14, default='#')
    logo = StdImageField('Logo',upload_to='logo_mover',variations={'thumb':
         {'width':300,'height':300,'crop':True }},null=True, default=None)

    class Meta:
        verbose_name = 'IGREJA'
        verbose_name_plural = 'IGREJAS'

    def __str__(self):
        return self.link_cadastro


# create_main.py

class Parceiros(Base):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    cpf_cnpj = models.CharField(max_length=14)  # CPF ou CNPJ
    phone = models.CharField(max_length=15, blank=True, null=True)  # Telefone opcional
    description = models.TextField(blank=True, null=True)  # Descrição opcional
    
    class Meta:
        verbose_name = 'Parceiro'
        verbose_name_plural = 'Parceiros'


    def __str__(self):
        return self.name