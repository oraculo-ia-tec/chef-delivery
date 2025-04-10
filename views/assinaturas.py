import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import stripe
from datetime import datetime
import asyncio
from key_config import API_KEY_STRIPE, URL_BASE, STRIPE_WEBHOOK_SECRET


# Configurações do Stripe
stripe.api_key = API_KEY_STRIPE

app = FastAPI()

class Assinatura(BaseModel):
    customer_id: str
    price_id: str
    payment_method: str

class AssinaturaResponse(BaseModel):
    id: str
    customer: str
    status: str
    created: datetime
    current_period_end: datetime

async def criar_assinatura(assinatura: Assinatura):
    try:
        subscription = stripe.Subscription.create(
            customer=assinatura.customer_id,
            items=[{"price": assinatura.price_id}],
            default_payment_method=assinatura.payment_method,
        )
        return AssinaturaResponse(
            id=subscription['id'],
            customer=subscription['customer'],
            status=subscription['status'],
            created=datetime.fromtimestamp(subscription['created']),
            current_period_end=datetime.fromtimestamp(subscription['current_period_end'])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def listar_assinaturas(customer_id: str):
    try:
        subscriptions = stripe.Subscription.list(customer=customer_id)
        return [
            AssinaturaResponse(
                id=sub['id'],
                customer=sub['customer'],
                status=sub['status'],
                created=datetime.fromtimestamp(sub['created']),
                current_period_end=datetime.fromtimestamp(sub['current_period_end'])
            ) for sub in subscriptions.data
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subscriptions", response_model=AssinaturaResponse)
async def api_criar_assinatura(assinatura: Assinatura):
    return await criar_assinatura(assinatura)

@app.get("/subscriptions/{customer_id}", response_model=list[AssinaturaResponse])
async def api_listar_assinaturas(customer_id: str):
    return await listar_assinaturas(customer_id)

# Streamlit Interface
def criar_assinatura():
    st.title("Flash Pagamentos")

    # Seção para criar uma nova assinatura
    st.header("Criar Assinatura")
    with st.form(key='create_assinatura'):
        customer_id = st.text_input("ID do Cliente")
        price_id = st.text_input("ID do Preço")  # ID do preço que você configurou no Stripe
        payment_method = st.text_input("ID do Método de Pagamento")  # ID do método de pagamento
        submit_button = st.form_submit_button("Criar Assinatura")

        if submit_button:
            nova_assinatura = Assinatura(
                customer_id=customer_id,
                price_id=price_id,
                payment_method=payment_method
            )
            try:
                response = asyncio.run(criar_assinatura(nova_assinatura))
                st.success(f"Assinatura criada com sucesso! ID: {response.id}")
            except Exception as e:
                st.error(f"Erro ao criar assinatura: {e}")

    # Seção para listar assinaturas
    st.header("Listar Assinaturas")
    customer_id_listar = st.text_input("ID do Cliente para listar assinaturas")
    if st.button("Carregar Assinaturas"):
        if customer_id_listar:
            with st.spinner("Carregando lista de assinaturas..."):
                try:
                    assinaturas = asyncio.run(listar_assinaturas(customer_id_listar))
                    if assinaturas:
                        data = [{
                            'ID': assinatura.id,
                            'Cliente': assinatura.customer,
                            'Status': assinatura.status,
                            'Data de Criação': assinatura.created.strftime('%Y-%m-%d %H:%M:%S'),
                            'Próximo Vencimento': assinatura.current_period_end.strftime('%Y-%m-%d %H:%M:%S')
                        } for assinatura in assinaturas]
                        df = pd.DataFrame(data)
                        st.dataframe(df)  # Exibe a tabela de assinaturas no Streamlit
                    else:
                        st.warning("Nenhuma assinatura encontrada.")
                except Exception as e:
                    st.error(f"Erro ao carregar assinaturas: {e}")
        else:
            st.warning("Por favor, insira o ID do cliente.")
