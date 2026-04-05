import os
from dotenv import load_dotenv

load_dotenv()

# URL base da API do Stripe
URL_BASE_STRIPE = os.getenv("URL_BASE_STRIPE", "https://api.stripe.com/v1")
URL_BASE_ASAAS = os.getenv(
    "BASE_URL_ASAAS", "https://api-sandbox.asaas.com/v3")

# Chave da API do Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Chave da API do Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Chave da API do Stripe
API_KEY_STRIPE = os.getenv("API_KEY_STRIPE", "")

# Chave do Webhook do Stripe
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Chave do Webhook do MAKE CADASTRO
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Chave do Webhook do MAKE AGENDA
WEBHOOK_AGENDA = os.getenv("WEBHOOK_AGENDA", "")

# Chave do Webhook do MAKE TESTE
WEBHOOK_TESTE = os.getenv("WEBHOOK_TESTE", "")

# Chave do Webhook do MAKE CADASTRO
WEBHOOK_CADASTRO = os.getenv("WEBHOOK_CADASTRO", "")
