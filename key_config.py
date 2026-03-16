import streamlit as st

_api = st.secrets.get("api_keys", {})
_urls = st.secrets.get("urls", {})

# URL base da API do Stripe
URL_BASE_STRIPE = _urls.get("URL_BASE_STRIPE", "https://api.stripe.com/v1")
URL_BASE_ASAAS = _urls.get("BASE_URL_ASAAS", "https://api-sandbox.asaas.com/v3")

# Chave da API do Groq
GROQ_API_KEY = _api.get("GROQ_API_KEY", "")

# Chave da API do Banco de Dados
DATABASE_URL = _api.get("DATABASE_URL", "")

# Chave da API do Stripe
API_KEY_STRIPE = _api.get("API_KEY_STRIPE", "")

# Chave do Webhook do Stripe
STRIPE_WEBHOOK_SECRET = _api.get("STRIPE_WEBHOOK_SECRET", "")

# Chave do Webhook do MAKE CADASTRO
WEBHOOK_URL = _api.get("WEBHOOK_URL", "")

# Chave do Webhook do MAKE AGENDA
WEBHOOK_AGENDA = _api.get("WEBHOOK_AGENDA", "")

# Chave do Webhook do MAKE TESTE
WEBHOOK_TESTE = _api.get("WEBHOOK_TESTE", "")

# Chave do Webhook do MAKE CADASTRO
WEBHOOK_CADASTRO = _api.get("WEBHOOK_CADASTRO", "")