import os
import re
import streamlit as st
import requests  # pip install requests
import pandas as pd
import datetime
import asyncio
import uuid
import base64
from datetime import date, timedelta

from api_asaas import streamlit_payment_flow_example
from configuracao import ASAAS_API_KEY, ASAAS_ENVIRONMENT


WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


def is_valid_email(email):
    # Basic regex pattern for email validation
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None


def contact_form():
    with st.form("contact_form"):
        name = st.text_input("Nome e Sobrenome")
        email = st.text_input("E-mail")
        message = st.text_area("Envie uma mensagem")
        submit_button = st.form_submit_button("ENVIAR")

    if submit_button:
        if not WEBHOOK_URL:
            st.error(
                "Email service is not set up. Please try again later.", icon="📧")
            st.stop()

        if not name:
            st.error("Please provide your name.", icon="🧑")
            st.stop()

        if not email:
            st.error("Please provide your email address.", icon="📨")
            st.stop()

        if not is_valid_email(email):
            st.error("Please provide a valid email address.", icon="📧")
            st.stop()

        if not message:
            st.error("Please provide a message.", icon="💬")
            st.stop()

        # Prepare the data payload and send it to the specified webhook URL
        data = {"email": email, "name": name, "message": message}
        response = requests.post(WEBHOOK_URL, json=data)

        if response.status_code == 200:
            st.success("A sua mensagem foi enviada com sucesso! 🎉", icon="🚀")
        else:
            st.error(
                "Desculpe-me, parece que houve um problema no envio da sua mensagem", icon="😨")


def cadastro_pedido():
    with st.form("cadastro_pedido"):
        name = st.text_input("Nome")
        whatsapp = st.text_input("WhatsApp")
        endereco = st.text_input("Endereço")
        total_pedido = st.number_input(
            "Total do Pedido (R$)", min_value=0.01, step=0.01, format="%.2f",
            value=float(st.session_state.get("total_value", 0.0)) or 0.01,
        )
        message = st.text_area("Envie uma observação")
        submit_button = st.form_submit_button("FINALIZAR PEDIDO")

    if submit_button:
        if not name:
            st.error("Qual o seu nome?", icon="🧑")
            st.stop()

        if not whatsapp:
            st.error("Digite seu WhatsApp.", icon="📨")
            st.stop()

        if not endereco:
            st.error("Digite seu endereço com o nome do bairro.", icon="📨")
            st.stop()

        if total_pedido <= 0:
            st.error("O valor total do pedido deve ser maior que zero.", icon="💰")
            st.stop()

        # Salva os dados no session_state
        st.session_state["name"] = name
        st.session_state["whatsapp"] = whatsapp
        st.session_state["endereco"] = endereco
        st.session_state["observacao"] = message
        st.session_state["total_value"] = total_pedido

        # --- Gera cobrança PIX via ASAAS ---
        if ASAAS_API_KEY:
            try:
                order_id = f"CHEF-{uuid.uuid4().hex[:8].upper()}"
                due_date = (date.today() + timedelta(days=1)).isoformat()

                with st.spinner("Gerando cobrança PIX..."):
                    result = asyncio.run(streamlit_payment_flow_example(
                        st.session_state,
                        api_key=ASAAS_API_KEY,
                        environment=ASAAS_ENVIRONMENT,
                        due_date=due_date,
                        order_id=order_id,
                        total_value=total_pedido,
                        payment_method="pix",
                    ))

                st.success("Cobrança PIX gerada com sucesso!", icon="✅")

                # Exibe QR Code PIX
                if result.get("pix_qr_code_base64"):
                    qr_bytes = base64.b64decode(result["pix_qr_code_base64"])
                    st.image(
                        qr_bytes, caption="Escaneie o QR Code para pagar", width=300)

                # Exibe código PIX copia-e-cola
                if result.get("pix_payload"):
                    st.text_area(
                        "PIX Copia e Cola",
                        value=result["pix_payload"],
                        height=100,
                        help="Copie este código e cole no app do seu banco",
                    )

                # Exibe informações do pagamento
                if result.get("pix_expiration_date"):
                    st.info(
                        f"⏰ Validade do PIX: {result['pix_expiration_date']}")

                if result.get("payment_id"):
                    st.caption(f"ID do pagamento: {result['payment_id']}")

            except Exception as e:
                st.error(f"Erro ao gerar cobrança PIX: {e}", icon="❌")
                st.info(
                    "Seu pedido foi registrado. Entre em contato pelo WhatsApp para combinar o pagamento.")
        else:
            st.warning(
                "Sistema de pagamento não configurado. Entre em contato para combinar o pagamento.", icon="⚠️")

        # --- Envia dados para o webhook (MAKE/automação) ---
        if WEBHOOK_URL:
            data = {"Nome": name, "WhatsApp": whatsapp, "Endereço": endereco}
            try:
                response = requests.post(WEBHOOK_URL, json=data)
                if response.status_code == 200:
                    st.success("Pedido registrado com sucesso! 🎉", icon="🚀")
                else:
                    st.error(
                        "Desculpe-me, parece que houve um problema no envio do pedido", icon="😨")
            except requests.RequestException:
                st.error("Erro ao conectar com o servidor de pedidos.", icon="😨")


# Variável para armazenar o estado do pedido
pedido_finalizado = False
