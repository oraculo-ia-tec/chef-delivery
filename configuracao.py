# configuracao.py
import streamlit as st


BASE_URL = st.secrets.get("urls", {}).get(
    "BASE_URL_ASAAS", "https://sandbox.asaas.com/api/v3")

GROQ_API_KEY = st.secrets["api_keys"]["GROQ_API_KEY"]

ASAAS_API_KEY = st.secrets.get("api_keys", {}).get("ASAAS_API_KEY", "")

ASAAS_ENVIRONMENT = "sandbox"  # Altere para "production" em produção
