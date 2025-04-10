import asyncio
import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import EmailStr, BaseModel
import pandas as pd
import httpx
from key_config import API_KEY_STRIPE, URL_BASE
from decouple import config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime


# Configuração do banco de dados
DATABASE_URL = config("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def verificar_usuario(username, password):
    with engine.connect() as connection:
        query = text(
            "SELECT username, password, role FROM oraculo_user WHERE username = :username AND password = :password")
        result = connection.execute(query, {"username": username, "password": password})
        user = result.fetchone()
        if user:
            return {
                'username': user[0],
                'password': user[1],
                'role': user[2]
            }
    return None


app = FastAPI()


# Modelo de Parceiro
class ParceiroCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    cpf: str
    birthday: str
    address_line1: str
    address_city: str
    address_state: str
    address_postal_code: str


class ParceiroResponse(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str


async def criar_parceiro_no_stripe(parceiro: ParceiroCreate):
    url = f"{URL_BASE}/accounts"
    headers = {
        "Authorization": f"Bearer {API_KEY_STRIPE}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # Divida o nome do parceiro em primeiro e último nome
    parts = parceiro.nome.split()
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    # Ajuste de telefone
    telefone_formatado = f'+55{parceiro.telefone}'.strip()

    data = {
        "type": "express",
        "country": "BR",
        "email": parceiro.email,
        "capabilities[transfers]": "requested",
        "business_type": "individual",
        "individual[first_name]": first_name,
        "individual[last_name]": last_name,
        "individual[phone]": telefone_formatado,
        "individual[cpf]": parceiro.cpf
        # Adicione outros parâmetros necessários e formatados
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_details = exc.response.json().get('error', {}).get('message', 'Erro desconhecido')
        st.error(f"Erro ao criar parceiro: {error_details}")
        raise


@app.post("/parceiros", response_model=ParceiroResponse)
async def api_create_parceiro(parceiro: ParceiroCreate):
    try:
        novo_parceiro = await criar_parceiro_no_stripe(parceiro)
        return ParceiroResponse(
            id=novo_parceiro['id'],
            nome=parceiro.nome,
            email=parceiro.email,
            telefone=parceiro.telefone
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def fetch_parceiros(limit: int = 100, offset: int = 0):
    url = f"{URL_BASE}/accounts"
    headers = {
        "Authorization": f"Bearer {API_KEY_STRIPE}"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params={"limit": limit, "starting_after": offset})
            response.raise_for_status()
            parceiros = response.json().get('data', [])
            return [
                {
                    "id": account['id'],
                    "nome": account.get('business_profile', {}).get('name', 'Nome não disponível'),
                    "email": account.get('email', 'Email não disponível'),
                    "telefone": account.get('metadata', {}).get('telefone', 'Telefone não disponível')
                } for account in parceiros
            ]
    except httpx.HTTPStatusError as exc:
        error_details = exc.response.text
        st.error(f"Erro ao carregar parceiros: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@app.get("/parceiros", response_model=list[ParceiroResponse])
async def api_fetch_parceiros(limit: int = 100, offset: str = None):
    return await fetch_parceiros(limit=limit, offset=offset)



# Streamlit Interface
def showParceiro():
    st.title("Sistema Flash Pagamentos")
    st.header("Criar Novo Parceiro")

    if 'nome' not in st.session_state: st.session_state['nome'] = ""
    if 'email' not in st.session_state: st.session_state['email'] = ""
    if 'telefone' not in st.session_state: st.session_state['telefone'] = ""
    if 'cpf' not in st.session_state: st.session_state['cpf'] = ""
    if 'birthday' not in st.session_state: st.session_state['birthday'] = ""
    if 'address_line1' not in st.session_state: st.session_state['address_line1'] = ""
    if 'address_city' not in st.session_state: st.session_state['address_city'] = ""
    if 'address_state' not in st.session_state: st.session_state['address_state'] = ""
    if 'address_postal_code' not in st.session_state: st.session_state['address_postal_code'] = ""

    with st.form(key='form_parceiro'):
        nome = st.text_input("Nome:", value=st.session_state.nome)
        email = st.text_input("E-mail:", value=st.session_state.email)
        telefone = st.text_input("Telefone:", value=st.session_state.telefone)
        cpf = st.text_input("CPF:", value=st.session_state.cpf)
        birthday = st.text_input("Data de Nascimento (YYYY-MM-DD):", value=st.session_state.birthday)

        # Converte a data para o formato necessário, se necessário
        try:
            data_convertida = datetime.strptime(birthday.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
            st.session_state['birthday'] = data_convertida
        except ValueError:
            st.error("Formato de data inválido! Use YYYY-MM-DD.")

        address_line1 = st.text_input("Endereço:", value=st.session_state.address_line1)
        address_city = st.text_input("Cidade:", value=st.session_state.address_city)
        address_state = st.text_input("Estado:", value=st.session_state.address_state)
        address_postal_code = st.text_input("Código Postal:", value=st.session_state.address_postal_code)

        submit_button = st.form_submit_button("CRIAR PARCEIRO!")

        if submit_button:
            parceiro = ParceiroCreate(
                nome=nome,
                email=email,
                telefone=telefone,
                cpf=cpf,
                birthday=data_convertida,
                address_line1=address_line1,
                address_city=address_city,
                address_state=address_state,
                address_postal_code=address_postal_code
            )
            try:
                resultado = asyncio.run(api_create_parceiro(parceiro))
                st.success(f"Parceiro {resultado.nome} criado com sucesso!")
                # Limpa os campos após a criação
                st.session_state.nome = ""
                st.session_state.email = ""
                st.session_state.telefone = ""
                st.session_state.cpf = ""
                st.session_state.birthday = ""
                st.session_state.address_line1 = ""
                st.session_state.address_city = ""
                st.session_state.address_state = ""
                st.session_state.address_postal_code = ""
            except Exception as e:
                st.error(f"Erro ao criar parceiro: {e}")

    st.header("Parceiros da ORÁCULOS IA")
    limit = st.number_input("Limite", min_value=1, max_value=100, value=10)

    with st.expander("Listar Parceiros"):
        if st.button("Listar"):
            try:
                parceiros = asyncio.run(api_fetch_parceiros(limit=limit))
                if parceiros:
                    data = [
                        {'ID': parceiro['id'], 'Nome': parceiro['nome'], 'E-mail': parceiro['email'],
                         'Telefone': parceiro['telefone']}
                        for parceiro in parceiros
                    ]
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.warning("Nenhum parceiro encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar parceiros: {e}")