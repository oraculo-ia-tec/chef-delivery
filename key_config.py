from decouple import config


# URL base da API do Stripe
BASE_URL_ASAAS = config("BASE_URL_ASAAS")

# URL base da API do Stripe
URL_BASE = "https://api.stripe.com/v1"

# Chave do MAKE DJANGO
DATABASE_URL = config("DATABASE_URL")


# Chave da API do Asaas
ASAAS_API_KEY = config("ASAAS_API_KEY")


# Chave da API do Stripe
API_KEY_STRIPE = config("API_KEY_STRIPE")


# Chave do Webhook do Stripe
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")


# Webhook do MAKE CADASTRO
WEBHOOK_CADASTRO = config("WEBHOOK_CADASTRO")


# Webhook do MAKE TESTE
WEBHOOK_TESTE = config("WEBHOOK_TESTE")


# Chave do Webhook do MAKE DJANGO
URL_DJANGO = config("URL_DJANGO")


# Chave do DJANGO
URL_DJANGO_TESTE = config("URL_DJANGO_TESTE")


# Chave do MAKE DJANGO
URL_DJANGO_NOVO_MEMBRO = config("URL_DJANGO_NOVO_MEMBRO")


# Chave do MAKE DJANGO
URL_DJANGO_ENQUETE = config("URL_DJANGO_ENQUETE")


# Chave do MAKE DJANGO
URL_DJANGO_RESPOSTA = config("URL_DJANGO_RESPOSTA")


TOKEN_API_DJANGO = config("TOKEN_API_DJANGO")


URL_TOKEN_API = config("URL_TOKEN_API")

