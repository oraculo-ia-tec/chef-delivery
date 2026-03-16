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
    description='FlashApi Pagamentos'
)


# Modelo de Pagamento
class Pagamento(BaseModel):
    id: str
    customer: str
    subscription: str
    payment_method: str
    payment_date: str
    value: float
    status: str

# Função para fazer requisições à API do Asaas para pagamentos
async def fetch_payments():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.asaas.com/api/v3/payments',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()

@app.get('/payments',
         description='Retorna todos os pagamentos ou uma lista vazia.',
         summary='Retorna todos os pagamentos',
         response_model=List[Pagamento],
         response_description='Pagamentos encontrados com sucesso.')
async def get_payments():
    payments = await fetch_payments()
    return payments.get('data', [])

@app.get('/payments/{payment_id}')
async def get_payment(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento'), db: Any = Depends()):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/payments/{payment_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Pagamento não encontrado.'
            )
        response.raise_for_status()
        return response.json()

@app.post('/payments', status_code=status.HTTP_201_CREATED, response_model=Pagamento)
async def post_payment(payment: Pagamento):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://www.asaas.com/api/v3/payments',
            json=payment.dict(),
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()

@app.put('/payments/{payment_id}')
async def put_payment(payment_id: str, payment: Pagamento):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f'https://www.asaas.com/api/v3/payments/{payment_id}',
            json=payment.dict(),
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe um pagamento com id {payment_id}')
        response.raise_for_status()
        return response.json()

@app.delete('/payments/{payment_id}')
async def delete_payment(payment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f'https://www.asaas.com/api/v3/payments/{payment_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe um pagamento com id {payment_id}')
        return Response(status_code=status.HTTP_204_NO_CONTENT)