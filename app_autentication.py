import streamlit as st
import httpx
import asyncio

API_BASE_URL = "http://localhost:8000"  # URL base da sua API FastAPI


async def register_user(email: str, password: str, role: str, cpf: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/register", json={
            "email": email,
            "password": password,
            "role": role,
            "cpf": cpf
        })
        response.raise_for_status()
        return response.json()


async def login_user(email: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/login", json={
            "email": email,
            "password": password
        })
        response.raise_for_status()
        return response.json()


def show_registration_form():
    st.title("Registro de Autor")
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type='password')
    role = st.selectbox("Função", ["Admin", "Parceiro", "Cliente"])
    cpf = st.text_input("CPF")

    if st.button("Registrar"):
        try:
            result = asyncio.run(register_user(email, password, role, cpf))
            st.success(result["message"])
        except Exception as e:
            st.error(f"Erro ao registrar: {e}")


def show_login_form():
    st.title("Login de Autor")
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type='password')

    if st.button("Fazer Login"):
        try:
            result = asyncio.run(login_user(email, password))
            st.success(result["message"])
            st.session_state.author_id = result["author_id"]  # Armazenar ID do autor na sessão
        except Exception as e:
            st.error(f"Erro ao fazer login: {e}")


def main():
    st.sidebar.title("Navegação")
    app_mode = st.sidebar.selectbox("Escolha o modo", ["Registrar", "Login"])

    if app_mode == "Registrar":
        show_registration_form()
    elif app_mode == "Login":
        show_login_form()

if __name__ == "__main__":
    main()
