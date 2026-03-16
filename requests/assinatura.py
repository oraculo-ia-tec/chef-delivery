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
    description='FlashApi Assinatura'
)


# Modelo de Assinatura
class Assinatura(BaseModel):
    id: str
    customer: str
    plan: str
    start_at: str
    billing_type: str
    status: str

# Função para fazer requisições à API do Asaas para assinaturas
async def fetch_subscriptions():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.asaas.com/api/v3/subscriptions',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()

@app.get('/subscriptions',
         description='Retorna todas as assinaturas ou uma lista vazia.',
         summary='Retorna todas as assinaturas',
         response_model=List[Assinatura],
         response_description='Assinaturas encontradas com sucesso.')
async def get_subscriptions():
    subscriptions = await fetch_subscriptions()
    return subscriptions.get('data', [])

@app.get('/subscriptions/{subscription_id}')
async def get_subscription(subscription_id: str = Path(default=None, title='ID da assinatura', description='ID da assinatura'), db: Any = Depends()):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/subscriptions/{subscription_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Assinatura não encontrada.'
            )
        response.raise_for_status()
        return response.json()

@app.post('/subscriptions', status_code=status.HTTP_201_CREATED, response_model=Assinatura)
async def post_subscription(subscription: Assinatura):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://www.asaas.com/api/v3/subscriptions',
            json=subscription.dict(),
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()

@app.put('/subscriptions/{subscription_id}')
async def put_subscription(subscription_id: str, subscription: Assinatura):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f'https://www.asaas.com/api/v3/subscriptions/{subscription_id}',
            json=subscription.dict(),
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe uma assinatura com id {subscription_id}')
        response.raise_for_status()
        return response.json()

@app.delete('/subscriptions/{subscription_id}')
async def delete_subscription(subscription_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f'https://www.asaas.com/api/v3/subscriptions/{subscription_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe uma assinatura com id {subscription_id}')
        return Response(status_code=status.HTTP_204_NO_CONTENT)