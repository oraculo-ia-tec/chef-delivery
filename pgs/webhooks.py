import streamlit as st
# ...existing code...


@app.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(webhook_id: int):
    for webhook in webhooks_db:
        if webhook.id == webhook_id:
            return webhook
    raise HTTPException(status_code=404, detail="Webhook not found")


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int):
    global webhooks_db
    webhooks_db = [webhook for webhook in webhooks_db if webhook.id != webhook_id]
    return {"message": "Webhook deleted successfully"}


async def shoWebhooks():
    st.title("Gerenciar Webhooks")

    # Seção para criar um novo webhook
    st.header("Criar Webhook")
    with st.form(key='create_webhook'):
        name = st.text_input("Nome do Webhook")  # Adicionado campo para nome do webhook
        url = st.text_input("URL do Webhook")
        event = st.text_input("Evento que aciona o webhook")
        enabled = st.checkbox("Ativo", value=True)
        submit_button = st.form_submit_button("Criar Webhook")

        if submit_button:
            webhook_data = {
                "name": name,  # Incluindo o nome na criação do webhook
                "url": url,
                "event": event,
                "enabled": enabled
            }
            response = requests.post(f"http://localhost:8000/webhooks/", json=webhook_data)  # Ajuste o BASE_URL conforme necessário
            if response.status_code == 200:
                st.success(f"Webhook criado com sucesso! ID: {response.json()['id']}")
            else:
                st.error("Erro ao criar webhook.")

    # Seção para listar webhooks
    st.header("Listar Webhooks")
    if st.button("Carregar Webhooks"):
        with st.spinner("Carregando lista de webhooks..."):
            response = requests.get(f"http://localhost:8000/webhooks/")  # Ajuste o BASE_URL conforme necessário
            if response.status_code == 200:
                webhooks = response.json()
                if webhooks:
                    df = pd.DataFrame(webhooks)
                    st.dataframe(df)  # Exibe a tabela de webhooks no Streamlit
                else:
                    st.warning("Nenhum webhook encontrado.")
            else:
                st.error("Erro ao carregar webhooks.")

