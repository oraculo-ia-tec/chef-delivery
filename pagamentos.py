import streamlit as st
import requests
import pandas as pd
from decouple import config



# Configuração da API do Asaas
#key_asaas = config('ASAAS_API_KEY')
key_asaas = '$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjdmYzUzNThhLWY5ZWItNDEyYy04NWNmLTdlNmJkNTZjYjhlNzo6JGFhY2hfMmRkZjFiYWMtZGNjMS00MDNkLWFjOTEtOTA2YTUzNWViYTY5'
BASE_URL = "https://api-sandbox.asaas.com/v3/payments"  # Endpoint correto
print(BASE_URL)
print(key_asaas)

# Função para buscar pagamentos da API do Asaas com base no status
def obter_pagamentos_da_api(status=None):
    try:
        # Verificar se o token está configurado corretamente
        if not key_asaas or key_asaas.strip() == "":
            st.error("❌ Erro: O token de acesso (ASAAS_API_KEY) não está configurado corretamente.")
            return []

        headers = {
            "Authorization": f"Bearer {key_asaas}"  # Token de acesso
        }
        params = {}
        if status:
            params["status"] = status  # Filtrar por status, se fornecido

        response = requests.get(BASE_URL, headers=headers, params=params)

        # Log da resposta da API
        st.write("Status Code:", response.status_code)
        st.write("Response Body:", response.text)

        # Validar resposta da API
        if response.status_code == 401:
            st.error("❌ Erro: Token de acesso inválido ou sem permissões. Verifique o token no painel do Asaas.")
            return []

        if response.status_code != 200:
            st.error(f"Erro ao buscar pagamentos: {response.text}")
            return []

        dados_pagamento = response.json()

        # Verificar se a resposta contém dados válidos
        if not dados_pagamento or 'data' not in dados_pagamento or not dados_pagamento['data']:
            st.warning("⚠️ A API retornou uma lista vazia. Verifique os filtros ou o status dos pagamentos.")
            return []

        return dados_pagamento.get('data', [])  # Retorna a lista de pagamentos

    except Exception as e:
        st.error(f"Erro ao conectar à API do Asaas: {str(e)}")
        return []


# Função auxiliar para exibir pagamentos em uma aba
def exibir_pagamentos(pagamentos_filtrados, tab):
    with tab:
        if not pagamentos_filtrados:
            st.warning("⚠️ Nenhum pagamento registrado.")
        else:
            # Converte os dados dos pagamentos para um DataFrame
            pagamentos_data = [
                {
                    "ID": pagamento['id'],
                    "Usuário ID": pagamento['customer'],
                    "Valor": float(pagamento['value']),
                    "Status": pagamento['status'],
                    "Método de Pagamento": pagamento['billingType'].capitalize(),
                    "Data de Criação": pagamento['dateCreated'][:10],  # Formato YYYY-MM-DD
                    "Data de Vencimento": pagamento['dueDate'][:10],  # Formato YYYY-MM-DD
                    "Hora do Pagamento": pagamento.get('paymentDate', "Não pago")[:10],  # Formato YYYY-MM-DD ou "Não pago"
                }
                for pagamento in pagamentos_filtrados
            ]

            df = pd.DataFrame(pagamentos_data)

            # Pesquisa por ID do pagamento ou usuário
            pesquisa = st.chat_input("🔍 Pesquisar por ID do pagamento ou Usuário ID (digite os 3 primeiros caracteres)")
            if pesquisa and len(pesquisa) >= 3:
                df = df[df["ID"].astype(str).str.startswith(pesquisa, na=False) |
                        df["Usuário ID"].astype(str).str.startswith(pesquisa, na=False)]

            # Exibe o DataFrame
            st.dataframe(df)

            # Exibir detalhes de um pagamento selecionado, se necessário
            if not df.empty:
                st.subheader("Detalhes do Pagamento Selecionado")
                pagamento_selecionado = st.selectbox("Selecione um pagamento:", df["ID"])
                pagamento = next((p for p in pagamentos_filtrados if str(p['id']) == pagamento_selecionado), None)

                if pagamento:
                    st.write(f"**Valor:** R$ {pagamento['value']:.2f}")
                    st.write(f"**Status:** {pagamento['status']}")
                    st.write(f"**Método de Pagamento:** {pagamento['billingType'].capitalize()}")
                    st.write(f"**Data de Criação:** {pagamento['dateCreated'][:10]}")
                    st.write(f"**Data de Vencimento:** {pagamento['dueDate'][:10]}")
                    st.write(f"**Hora do Pagamento:** {pagamento.get('paymentDate', 'Não pago')[:10]}")


# Interface principal do Streamlit
def show_pagamentos():
    # 📊 **Aba de Listagem de Pagamentos**
    st.title("💰 Gestão de Pagamentos")
    tabs = st.tabs(["💳 Todos os Pagamentos", "⏳ Pendentes", "✅ Pagos", "❌ Cancelados"])
    tab_todos, tab_pendentes, tab_pagos, tab_cancelados = tabs

    # Buscar pagamentos da API
    pagamentos_todos = obter_pagamentos_da_api()  # Todos os pagamentos
    pagamentos_pendentes = obter_pagamentos_da_api(status="PENDING")  # Pagamentos pendentes
    pagamentos_pagos = obter_pagamentos_da_api(status="RECEIVED")  # Pagamentos pagos
    pagamentos_cancelados = obter_pagamentos_da_api(status="CANCELED")  # Pagamentos cancelados

    # Exibir pagamentos em cada aba
    exibir_pagamentos(pagamentos_todos, tab_todos)
    exibir_pagamentos(pagamentos_pendentes, tab_pendentes)
    exibir_pagamentos(pagamentos_pagos, tab_pagos)
    exibir_pagamentos(pagamentos_cancelados, tab_cancelados)
