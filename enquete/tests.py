from django.test import TestCase
from key_config import TOKEN_API_DJANGO, URL_TOKEN_API
import requests
import streamlit as st
from typing import Optional, Dict

def obter_token(username: str, password: str) -> str:
    """Obtém o token de autenticação da API."""
    url = URL_TOKEN_API
    response = requests.post(url, json={"username": username, "password": password})

    if response.status_code == 200:
        return response.json().get("token")
    else:
        st.error("Erro ao obter token de autenticação.")
        return None


def verificar_token(token: str) -> Optional[Dict]:
    """Verifica se o token de autenticação é válido."""
    url = URL_TOKEN_API  # Endpoint que valida o token
    headers = {'Authorization': f'Token {TOKEN_API_DJANGO}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Retorna os dados do usuário
    else:
        st.error("Token inválido ou expirado.")
        return None


# Defina as credenciais a serem testadas
username = "william"
password = "oia2025"

# Chame a função para obter o token
token = obter_token(username, password)

# Verifique se o token foi obtido com sucesso
if token:
    print("Token obtido com sucesso:", token)
else:
    print("Falha ao obter token. Verifique suas credenciais.")
