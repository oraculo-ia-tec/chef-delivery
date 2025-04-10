from django.db import models


class Cargo(models.Model):
    """Tabela que armazena os papéis disponíveis na igreja."""

    CARGOS_CHOICES = [
        ('admin', 'Admin'),
        ('pastor', 'Pastor'),
        ('lider', 'Líder'),
        ('colaborador', 'Colaborador'),
        ('membro', 'Membro')
    ]

    nome = models.CharField(max_length=20, choices=CARGOS_CHOICES, unique=True)

    def __str__(self):
        return self.get_nome_display()  # Mostra o nome amigável do cargo


class User(models.Model):
    name = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=20)
    email = models.EmailField()
    whatsapp = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    cep = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)

    cargo = models.CharField(max_length=20, choices=Cargo.CARGOS_CHOICES)  # Agora é um CharField

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to="./src/img/membro", blank=True, null=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.name
