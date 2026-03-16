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
    description='FLASHAPI Webhooks'
)


from fastapi import FastAPI, Request, Response
import json

app = FastAPI()

@app.post('/webhooks/asaas', status_code=status.HTTP_200_OK)
async def handle_webhook(request: Request):
    # Verificar se a requisição é válida
    if request.headers.get('X-Asaas-Signature') != 'YOUR_WEBHOOK_SECRET':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Assinatura inválida')

    # Obter o corpo da requisição
    body = await request.json()

    # Processar o evento
    if body['event'] == 'transaction_paid':
        # Tratar o pagamento da transação
        transaction_id = body['data']['transaction_id']
        print(f'Transação {transaction_id} paga com sucesso!')
    elif body['event'] == 'transaction_failed':
        # Tratar o erro da transação
        transaction_id = body['data']['transaction_id']
        print(f'Transação {transaction_id} falhou!')
    else:
        print(f'Evento desconhecido: {body["event"]}')

    # Retornar uma resposta OK
    return Response(status_code=status.HTTP_200_OK)
