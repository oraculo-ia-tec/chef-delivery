from decouple import config
import stripe

# URL base da API do Stripe
URL_BASE = "https://api.stripe.com/v1"

# Chave da API do Stripe
API_KEY_STRIPE = config("API_KEY_STRIPE")
if not API_KEY_STRIPE:
    raise ValueError("A chave da API do Stripe não está definida. Verifique o arquivo .env.")

# Chave do Webhook do Stripe
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
if not STRIPE_WEBHOOK_SECRET:
    raise ValueError("A chave do Webhook não foi encontrada. Verifique a configuração.")

# Chave do Webhook do MAKE CADASTRO
WEBHOOK_URL = config("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("A chave do Webhook não foi encontrada. Verifique a configuração.")

# Chave do Webhook do MAKE AGENDA
WEBHOOK_AGENDA = config("WEBHOOK_AGENDA")
if not WEBHOOK_URL:
    raise ValueError("A chave do Webhook não foi encontrada. Verifique a configuração.")

# Chave do Webhook do MAKE TESTE
WEBHOOK_TESTE = config("WEBHOOK_TESTE")
if not WEBHOOK_AGENDA:
    raise ValueError("A chave do Webhook não foi encontrada. Verifique a configuração.")
