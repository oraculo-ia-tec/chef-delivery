import streamlit as st
# ...existing code...
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