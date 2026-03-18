import streamlit as st
# ...existing code...

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