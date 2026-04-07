import os
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
except Exception:
    st = None


def _is_streamlit_cloud() -> bool:
    return bool(
        os.getenv("STREAMLIT_CLOUD")
        or os.getenv("IS_STREAMLIT_CLOUD")
        or os.getenv("STREAMLIT_SHARING_MODE")
    )


def _from_secrets(path: str) -> Optional[Any]:
    if st is None:
        return None
    try:
        current = st.secrets
        for part in path.split("."):
            current = current[part]
        return current
    except Exception:
        return None


def get_config(env_key: str, secret_path: Optional[str] = None, default: Any = "") -> Any:
    if _is_streamlit_cloud() and secret_path:
        value = _from_secrets(secret_path)
        if value not in (None, ""):
            return value

    env_value = os.getenv(env_key)
    if env_value not in (None, ""):
        return env_value

    if secret_path:
        value = _from_secrets(secret_path)
        if value not in (None, ""):
            return value

    return default


DATABASE_URL = get_config("DATABASE_URL", "default.DATABASE_URL", "sqlite+aiosqlite:///chef_delivery.db")

GROQ_API_KEY = get_config("GROQ_API_KEY", "groq.GROQ_API_KEY", "")

EMAIL_REMETENTE = get_config("EMAIL_REMETENTE", "email.EMAIL_REMETENTE", "")
GOOGLE_CLIENT_ID = get_config("GOOGLE_CLIENT_ID", "email.GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = get_config("GOOGLE_CLIENT_SECRET", "email.GOOGLE_CLIENT_SECRET", "")
GOOGLE_OAUTH_SCOPES = get_config("GOOGLE_OAUTH_SCOPES", "email.GOOGLE_OAUTH_SCOPES", "https://www.googleapis.com/auth/gmail.send")
GOOGLE_OAUTH_CLIENT_TYPE = get_config("GOOGLE_OAUTH_CLIENT_TYPE", "email.GOOGLE_OAUTH_CLIENT_TYPE", "web")
GOOGLE_REDIRECT_URI = get_config("GOOGLE_REDIRECT_URI", "email.GOOGLE_REDIRECT_URI", "http://127.0.0.1:8765/")
GOOGLE_AUTH_PORT = get_config("GOOGLE_AUTH_PORT", "email.GOOGLE_AUTH_PORT", "8765")
GOOGLE_TOKEN_FILE = get_config("GOOGLE_TOKEN_FILE", "email.GOOGLE_TOKEN_FILE", "./tokens.json")
GMAIL_REFRESH_TOKEN = get_config("GMAIL_REFRESH_TOKEN", "email.GMAIL_REFRESH_TOKEN", "")

URL_BASE_STRIPE = get_config("URL_BASE_STRIPE", None, "https://api.stripe.com/v1")
API_KEY_STRIPE = get_config("API_KEY_STRIPE", None, "")
STRIPE_WEBHOOK_SECRET = get_config("STRIPE_WEBHOOK_SECRET", None, "")

BASE_URL_ASAAS = get_config("BASE_URL_ASAAS", None, "https://api-sandbox.asaas.com/v3")
ASAAS_API_KEY = get_config("ASAAS_API_KEY", None, "")
ASAAS_ENVIRONMENT = get_config("ASAAS_ENVIRONMENT", None, "sandbox")
WEBHOOK_PAY_ASAAS = get_config("WEBHOOK_PAY_ASAAS", None, "")

WEBHOOK_URL = get_config("WEBHOOK_URL", None, "")
WEBHOOK_AGENDA = get_config("WEBHOOK_AGENDA", None, "")
WEBHOOK_TESTE = get_config("WEBHOOK_TESTE", None, "")
WEBHOOK_CADASTRO = get_config("WEBHOOK_CADASTRO", None, "")

THEME_BASE = get_config("THEME_BASE", "theme.base", "dark")
