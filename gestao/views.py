from django.contrib import messages
from django.views.generic import TemplateView, FormView, DetailView, View, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from .forms import CadastroForm
from .models import Eventos, Parceiros
from django.views.decorators.csrf import csrf_protect
from .models import Lideres, Departamentos, Mentorias, Professores, Celulas, Igrejas
import stripe
from django.shortcuts import render, redirect
from django.http import JsonResponse
from key_config import API_KEY_STRIPE
from oraculo.models import Cargo, User


class IndexView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['igrejas'] = Igrejas.objects.all()

        return context


class CursoView(TemplateView):
    template_name = 'cursos.html'


class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class CadastroView(FormView):
    template_name = 'cadastro.html'
    form_class = CadastroForm
    success_url = reverse_lazy('registrar.html')

    def form_valid(self, form, *args, **kwargs):
        form.send_mail()
        messages.success(self.request, 'Seu cadastro foi feito com successo!')
        return super(CadastroView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request,'Erro ao se cadastrar.')
        return super(CadastroView, self).form_invalid(form, *args, **kwargs)


class AcessaView(LoginView):
    template_name = 'acessa.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard.html')

    def get_success_url(self):
        next_page = self.request.POST.get('next')
        if next_page:
            return next_page
        return reverse('dashboard.html')

    def form_valid(self, form):
        # Obter as credenciais do formulário
        username = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # Verificar se o usuário existe no banco de dados
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            # Usuário autenticado com sucesso e ativo, fazer login
            login(self.request, user)
            return super().form_valid(form)
        else:
            # Usuário não autenticado ou inativo, adicione uma mensagem de erro ao formulário
            form.add_error(None, 'Credenciais inválidas')
            return self.form_invalid(form)


class EmpresasView(TemplateView):

    template_name = 'catalogo-digital.html'
    paginate_by = 5
    ordering = 'id'

    def get_context_data(self, **kwargs):

        context = super(EmpresasView, self).get_context_data(**kwargs)
        context['user'] = User.objects.all()
        context['igreja'] = Igrejas.objects.all()

        return context


class NetworkView(TemplateView):
    template_name = 'network-mentorias.html'


class QuemSomosView(TemplateView):
    template_name = 'quem-somos.html'


class EventoView(TemplateView):
    template_name = 'eventos.html'

    def get_context_data(self, **kwargs):
        context = super(EventoView, self).get_context_data(**kwargs)
        context['eventos'] = Eventos.objects.all()

        return context


def create_pareiro(request):
    if request.method == "POST":
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        cpf_cnpj = request.POST.get('cpf_cnpj')
        phone = request.POST.get('phone')
        description = request.POST.get('description')

        # Criação da subconta no Stripe
        account = stripe.Account.create(
            type='express',
            business_profile={
                "name": business_name,
                "email": email,
                "description": description
            },
            metadata={
                "cpf_cnpj": cpf_cnpj,
                "phone": phone
            }
        )

        # Salvar a subconta no banco de dados
        parceiro = Parceiros.objects.create(
            business_name=business_name,
            email=email,
            cpf_cnpj=cpf_cnpj,
            phone=phone,
            description=description
        )
        return redirect('subcontas')  # Redireciona para a página de listagem de subcontas

    return render(request, 'create_subaccount.html')


def list_subaccounts(request):
    subcontas = Parceiros.objects.all()
    return render(request, 'list_subaccounts.html', {'subcontas': subcontas})