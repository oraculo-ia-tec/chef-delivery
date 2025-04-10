import streamlit as st
import requests
import pandas as pd
from decouple import config  # Para carregar variáveis de ambiente

# Configuração da API do Asaas
BASE_URL = "https://api-sandbox.asaas.com/v3/payments"  # Endpoint correto

# Carregar o token de acesso de forma segura
key_asaas = config("ASAAS_API_KEY")  # Substitua pelo seu token no arquivo .env
print(key_asaas)

# Função para listar pagamentos
def listar_pagamentos():
    try:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {key_asaas}"
        }

        response = requests.get(BASE_URL, headers=headers)

        # Log da resposta da API
        st.write("Status Code:", response.status_code)
        st.write("Response Body:", response.text)

        if response.status_code == 401:
            st.error("❌ Erro: Token de acesso inválido ou sem permissões.")
            return []

        if response.status_code != 200:
            st.error(f"❌ Erro ao listar pagamentos: {response.status_code}")
            return []

        dados_pagamento = response.json()

        # Verificar se a resposta contém dados válidos
        if not dados_pagamento or 'data' not in dados_pagamento or not dados_pagamento['data']:
            st.warning("⚠️ Nenhum pagamento encontrado.")
            return []

        return dados_pagamento.get('data', [])  # Retorna a lista de pagamentos

    except Exception as e:
        st.error(f"❌ Erro ao conectar à API do Asaas: {str(e)}")
        return []


# Criação da interface Streamlit
st.title("📋 Lista de Pagamentos do Asaas")

# Botão para carregar pagamentos
if st.button("🔄 Carregar Pagamentos"):
    pagamentos = listar_pagamentos()

    if pagamentos:
        # Transformar a lista de pagamentos em um DataFrame
        df_pagamentos = pd.DataFrame(pagamentos)

        # Filtrar colunas relevantes
        colunas_relevantes = [
            "id", "customer", "value", "status", "billingType", "dateCreated", "dueDate", "paymentDate"
        ]
        df_pagamentos = df_pagamentos[colunas_relevantes]

        # Renomear colunas para facilitar a leitura
        df_pagamentos.rename(columns={
            "id": "ID",
            "customer": "Usuário ID",
            "value": "Valor",
            "status": "Status",
            "billingType": "Método de Pagamento",
            "dateCreated": "Data de Criação",
            "dueDate": "Data de Vencimento",
            "paymentDate": "Hora do Pagamento"
        }, inplace=True)

        # Formatar datas
        df_pagamentos["Data de Criação"] = pd.to_datetime(df_pagamentos["Data de Criação"]).dt.strftime('%Y-%m-%d')
        df_pagamentos["Data de Vencimento"] = pd.to_datetime(df_pagamentos["Data de Vencimento"]).dt.strftime('%Y-%m-%d')
        df_pagamentos["Hora do Pagamento"] = df_pagamentos["Hora do Pagamento"].fillna("Não pago").apply(
            lambda x: x[:10] if x != "Não pago" else x
        )

        # Exibir os dados em uma tabela
        st.dataframe(df_pagamentos)
    else:
        st.warning("⚠️ Nenhum pagamento encontrado.")