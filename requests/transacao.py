from typing import Dict, List, Optional, Any
from fastapi.responses import JSONResponse
from fastapi import Response, Path, Query, Header, FastAPI, HTTPException, status, Depends
from fastapi import HTTPException
from pydantic import BaseModel
import httpx
import streamlit as st

# Configuração da chave de acesso
api_key = st.secrets.get("api_keys", {}).get("API_KEY_ASAAS", "")
api_secret = st.secrets.get("api_keys", {}).get("API_SECRET_ASAAS", "")

app = FastAPI(
    title='FLASHAPI SISTEMA DE PAGAMENTOS',
    version='0.0.1',
    description='FlashApi Transações'
)

from pydantic import BaseModel
from fastapi import FastAPI, status, Body, HTTPException
import httpx

app = FastAPI()
api_key = "YOUR_API_KEY"


class Transacao(BaseModel):
    payment_id: str
    recipient_id: str
    recipient_type: str
    amount: float
    status: str


def calculate_commission(amount: float, recipient_type: str) -> float:
    if recipient_type == 'Parceiro':
        return amount * 0.30  # 30% no ato da assinatura
    elif recipient_type == 'Colaborador':
        return amount * 0.20  # 20% no ato da assinatura
    elif recipient_type == 'Consultor':
        return amount * 0.10  # 10% no ato da assinatura
    else:
        raise ValueError("Tipo de receptor desconhecido")


@app.post('/v3/transactions', status_code=status.HTTP_201_CREATED, response_model=Transacao)
async def create_transacao(transacao: Transacao = Body(...)):
    commission_amount = calculate_commission(transacao.amount, transacao.recipient_type)
    transacao.amount -= commission_amount  # Subtrair a comissão do valor da transação

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://www.asaas.com/api/v3/transactions',
            json=transacao.dict(),
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


@app.get('/v3/transactions/{transaction_id}', status_code=status.HTTP_200_OK, response_model=Transacao)
async def get_transacao(transaction_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/transactions/{transaction_id}',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


@app.put('/v3/transactions/{transaction_id}', status_code=status.HTTP_200_OK, response_model=Transacao)
async def update_transacao(transaction_id: str, transacao: Transacao = Body(...)):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f'https://www.asaas.com/api/v3/transactions/{transaction_id}',
            json=transacao.dict(),
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


@app.delete('/v3/transactions/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_transacao(transaction_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f'https://www.asaas.com/api/v3/transactions/{transaction_id}',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return Response(status_code=status.HTTP_204_NO_CONTENT)