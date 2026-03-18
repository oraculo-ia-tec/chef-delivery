import streamlit as st
# ...existing code...
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