from .models import ( Professores, Cultos, Lideres, Cursos, Pastores , Parceiros,
                     Departamentos, Eventos, Igrejas, Celulas, Colaboradores)
from django.core.mail.message import EmailMessage
from django import forms


class CadastroForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    empresa = forms.CharField(label='EMPRESA', max_length=100)
    cnpj = forms.CharField(label='CNPJ', max_length=20)
    endereco = forms.CharField(label='ENDEREÇO', max_length=200)
    whats = forms.CharField(label='WhatsApp', max_length=11)
    nome = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    senha = forms.CharField(label='SENHA', max_length=100)
    assunto = forms.CharField(label='Assunto', max_length=400)
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def send_mail(self):
        usuario = self.cleaned_data['usuario']
        empresa = self.cleaned_data['empresa']
        nome = self.cleaned_data['nome']
        whats = self.cleaned_data['whats']
        email = self.cleaned_data['email']
        senha = self.cleaned_data['senha']
        assunto = self.cleaned_data['assunto']

        conteudo = f'PARABÉNS PELO SEU CADASTRO {nome} FICAMOS MUITO FELIZ POR SE ASSOCIAR AO NOSSO MOVER! CLIQUE NO LINK ABAIXO' \
                   f'PARA CONFIRMAR SEU ACESSO\n' \
                    f'\nUsuário: {usuario}\nSenha: {senha}\nEmpresa: {empresa}\nE-mail:{whats}\nNome Responsável:{nome}\n' \
                   f'E-mail: {email}\nAssunto: {assunto}'

        mail = EmailMessage(
            subject=assunto,
            body=conteudo,
            from_email='mensagem@moverbrasiloficial.com.br',
            to=['william@flashdigital.tech',],
            headers={'Reply-To': email}
        )
        mail.send()


class LiderModelForms(forms.ModelForm):
    class Meta:
        model = Lideres
        fields = 'nome_lider','email','whats','bio', 'created_dt', 'updated_dt', 'active_dt'


class ProfessorModelForms(forms.Form):
    class Meta:
        model = Professores
        fields = '__all__'


class celulaModelForms(forms.Form):
    class Meta:
        model = Celulas
        fields = '__all__'


class CursoModelForms(forms.Form):
    class Meta:
        model = Cursos
        fields = '__all__'


class PastorModelForms(forms.Form):
    class Meta:
        model = Pastores
        fields = '__all__'


class ColaboradorModelForms(forms.Form):
    class Meta:
        model = Colaboradores
        fields = '__all__'


class DepartamentoModelForms(forms.Form):
    class Meta:
        model = Departamentos
        fields = '__all__'


class EventoModelForms(forms.Form):
    class Meta:
        model = Eventos
        fields = '__all__'


class IgrejaModelForms(forms.Form):
    class Meta:
        model = Igrejas
        fields = '__all__'


class PareiroForm(forms.ModelForm):
    class Meta:
        model = Parceiros
        fields = '__all__'