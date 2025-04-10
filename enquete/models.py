from django.db import models
from oraculo.models import Cargo, User


class Enquete(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    ativo = models.BooleanField(default=True)

    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    direcionado_a = models.ManyToManyField(Cargo, related_name="enquetes")  # Direcionamento por Cargo

    opcao1 = models.CharField(max_length=200, default='', blank=True)
    opcao2 = models.CharField(max_length=200, default='', blank=True)
    opcao3 = models.CharField(max_length=200, default='', blank=True)
    opcao4 = models.CharField(max_length=200, default='', blank=True)

    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    def get_roles(self):
        """Retorna os cargos direcionados à enquete"""
        return ", ".join(cargo.nome for cargo in self.direcionado_a.all())  # Exibe os nomes dos cargos


class Resposta(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='respostas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Referência ao modelo User
    resposta = models.CharField(max_length=255)
    explicacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('enquete', 'usuario')  # Cada usuário pode responder a uma enquete apenas uma vez

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    def __str__(self):
        return f'Resposta de {self.usuario.username} na enquete {self.enquete.titulo}'