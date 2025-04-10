import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User, Cargo


@csrf_exempt
@require_POST
def criar_usuario(request):
    """Criação de usuários no sistema."""
    try:
        # Carregar os dados da requisição
        data = json.loads(request.body)

        # 🔹 Validação de dados obrigatórios
        required_fields = ['name', 'cpf_cnpj', 'email', 'whatsapp', 'endereco', 'cep',
                           'bairro', 'cidade', 'cargo_id', 'username', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'status': 'fail', 'message': f'O campo {field} é obrigatório.'}, status=400)

        # 🔹 Buscar o cargo pelo ID
        try:
            cargo = Cargo.objects.get(id=data['cargo_id'])
        except Cargo.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Cargo inválido.'}, status=400)

        # 🔹 Criar usuário no banco de dados
        user = User.objects.create(
            name=data['name'],
            cpf_cnpj=data['cpf_cnpj'],
            email=data['email'],
            whatsapp=data['whatsapp'],
            endereco=data['endereco'],
            cep=data['cep'],
            bairro=data['bairro'],
            cidade=data['cidade'],
            cargo=cargo,  # 🔹 Associando ao objeto Cargo
            username=data['username']
        )

        # 🔹 Armazenar a senha de forma segura
        user.set_password(data['password'])
        user.save()

        # 🔹 Retornar sucesso com os dados cadastrados
        return JsonResponse({
            'status': 'success',
            'message': 'Usuário cadastrado com sucesso!',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'cargo': cargo.nome  # Exibir nome do cargo cadastrado
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'fail', 'message': 'Formato de dados inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': f'Erro interno: {str(e)}'}, status=500)


