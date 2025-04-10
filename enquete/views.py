
from .models import Enquete, Resposta
from oraculo.models import Cargo, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from datetime import datetime


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


@csrf_exempt
def criar_enquete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido. Use POST.'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado.'}, status=401)

    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado.'}, status=404)

    if user.cargo.nome not in ['admin', 'pastor']:
        return JsonResponse({'error': 'Acesso negado. Apenas administradores e pastores podem criar enquetes.'}, status=403)

    try:
        data = json.loads(request.body)

        # Verificando se os campos obrigatórios foram passados
        required_fields = ['titulo', 'descricao', 'data_inicio', 'data_fim']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'O campo {field} é obrigatório.'}, status=400)

        # Convertendo strings de data para objetos datetime
        try:
            data_inicio = datetime.fromisoformat(data['data_inicio'])
            data_fim = datetime.fromisoformat(data['data_fim'])
        except ValueError:
            return JsonResponse({'error': 'Formato de data inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS).'}, status=400)

        # Garantindo que `data_fim` seja depois de `data_inicio`
        if data_fim <= data_inicio:
            return JsonResponse({'error': 'A data de fim deve ser posterior à data de início.'}, status=400)

        # Obtendo os IDs dos cargos enviados na requisição
        cargos_ids = data.get('cargos', [])
        cargos_selecionados = Cargo.objects.filter(id__in=cargos_ids)

        if not cargos_selecionados.exists():
            return JsonResponse({'error': 'Nenhum cargo válido foi selecionado para a enquete.'}, status=400)

        # Criando a enquete
        enquete = Enquete.objects.create(
            titulo=data['titulo'],
            descricao=data['descricao'],
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=True,
            opcao1=data.get('opcao1', ''),
            opcao2=data.get('opcao2', ''),
            opcao3=data.get('opcao3', ''),
            opcao4=data.get('opcao4', ''),
            usuario=user  # Atribuindo o usuário que criou a enquete
        )

        # Associando a enquete aos cargos selecionados
        enquete.direcionado_a.set(cargos_selecionados)

        return JsonResponse({'success': 'Enquete criada com sucesso!'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Erro ao processar a requisição. Verifique o formato do JSON enviado.'}, status=400)

    except Exception as e:
        return JsonResponse({'error': f'Ocorreu um erro inesperado: {str(e)}'}, status=500)


def verificar_resposta(request, enquete_id):
    """Verifica se o usuário já respondeu à enquete."""
    if request.method == 'GET':
        username = request.GET.get('username')

        # Garante que busca na tabela correta
        user = get_object_or_404(User, username=username)
        enquete = get_object_or_404(Enquete, id=enquete_id)

        if Resposta.objects.filter(enquete=enquete, membro=user).exists():
            return JsonResponse({'ja_respondeu': True})
        return JsonResponse({'ja_respondeu': False})

    return JsonResponse({'error': 'Método não permitido.'}, status=405)




