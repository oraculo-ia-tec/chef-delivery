import asyncio
import os
from datetime import date, timedelta
from typing import Any

import streamlit as st
from groq import Groq

from api_asaas import (
    ChefDeliveryAsaasService,
    InMemoryPaymentRepository,
    build_asaas_client,
    create_payment_from_streamlit_session,
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_ENVIRONMENT = os.getenv("ASAAS_ENVIRONMENT", "sandbox")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


@st.cache_resource(show_spinner=False)
def get_payment_repository() -> InMemoryPaymentRepository:
    return InMemoryPaymentRepository()


def inicializar_session_state() -> None:
    campos = {
        "name": "",
        "primeiro_nome": "",
        "endereco": "",
        "whatsapp": "",
        "pedido": [],
        "observacao": "",
        "total_value": 0.0,
        "pedido_texto": "",
        "payment_result": None,
        "payment_error": "",
        "payment_method": "pix",
        "email": "",
        "cpf_cnpj": "",
        "postal_code": "",
        "address_number": "",
        "province": "",
        "remote_ip": "127.0.0.1",
        "current_order_id": "",
    }
    for campo, valor in campos.items():
        if campo not in st.session_state:
            st.session_state[campo] = valor


@st.cache_data(show_spinner=False)
def build_system_prompt(primeiro_nome: str) -> str:
    return f'''
Você é o Chef Delivery especialista em vendas online de carnes, bebidas e acompanhamentos.
Use o nome "{primeiro_nome}" quando existir.
Seja direto, claro e objetivo.

Fluxo obrigatório:
1. Descobrir o que o cliente deseja.
2. Informar preços e quantidades.
3. Confirmar total do pedido.
4. Coletar nome, endereço completo, WhatsApp e observações.
5. Ao final, orientar que o pagamento será gerado pelo sistema.

Regras:
- Não concluir pedido sem total definido.
- Sempre confirmar o resumo final do pedido.
- Quando faltar nome, endereço ou WhatsApp, peça esses dados.
- Quando o pedido estiver completo, diga para o cliente usar o painel de pagamento para gerar o PIX.
'''


def build_groq_response() -> str:
    if not client:
        return "GROQ_API_KEY não configurada."
    primeiro_nome = st.session_state.get("primeiro_nome") or "Cliente"
    messages = [
        {"role": "system", "content": build_system_prompt(primeiro_nome)}]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=500,
    )
    return completion.choices[0].message.content


def parse_order_fields_from_text(text: str) -> None:
    lower = text.lower()
    if "meu nome é" in lower:
        name = text.split("é", 1)[-1].strip()
        if name:
            st.session_state["name"] = name
            st.session_state["primeiro_nome"] = name.split()[0]
    if "rua" in lower or "avenida" in lower or "av." in lower:
        st.session_state["endereco"] = text.strip()
    if any(ch.isdigit() for ch in text) and ("zap" in lower or "whatsapp" in lower or len(''.join(filter(str.isdigit, text))) >= 10):
        digits = ''.join(filter(str.isdigit, text))
        if len(digits) >= 10:
            st.session_state["whatsapp"] = digits


def order_is_ready_for_payment() -> tuple[bool, list[str]]:
    missing = []
    if not st.session_state.get("name"):
        missing.append("nome")
    if not st.session_state.get("endereco"):
        missing.append("endereço")
    if not st.session_state.get("whatsapp"):
        missing.append("WhatsApp")
    if not st.session_state.get("pedido_texto") and not st.session_state.get("pedido"):
        missing.append("pedido")
    if float(st.session_state.get("total_value") or 0) <= 0:
        missing.append("total")
    return (len(missing) == 0, missing)


def render_order_capture_panel() -> None:
    st.subheader("🧾 Dados estruturados do pedido")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["name"] = st.text_input(
            "Nome", value=st.session_state.get("name", ""))
        if st.session_state["name"]:
            st.session_state["primeiro_nome"] = st.session_state["name"].split()[
                0]
        st.session_state["whatsapp"] = st.text_input(
            "WhatsApp", value=st.session_state.get("whatsapp", ""))
        st.session_state["email"] = st.text_input(
            "E-mail", value=st.session_state.get("email", ""))
        st.session_state["cpf_cnpj"] = st.text_input(
            "CPF/CNPJ", value=st.session_state.get("cpf_cnpj", ""))
    with col2:
        st.session_state["endereco"] = st.text_area(
            "Endereço completo", value=st.session_state.get("endereco", ""), height=120)
        st.session_state["postal_code"] = st.text_input(
            "CEP", value=st.session_state.get("postal_code", ""))
        st.session_state["address_number"] = st.text_input(
            "Número", value=st.session_state.get("address_number", ""))
        st.session_state["province"] = st.text_input(
            "Bairro", value=st.session_state.get("province", ""))

    st.session_state["pedido_texto"] = st.text_area(
        "Resumo do pedido", value=st.session_state.get("pedido_texto", ""), height=120)
    st.session_state["observacao"] = st.text_area(
        "Observação", value=st.session_state.get("observacao", ""), height=80)
    st.session_state["total_value"] = st.number_input("Total do pedido (R$)", min_value=0.0, step=0.01, value=float(
        st.session_state.get("total_value") or 0.0), format="%.2f")


async def generate_order_payment() -> dict[str, Any]:
    client_asaas = await build_asaas_client(api_key=ASAAS_API_KEY, environment=ASAAS_ENVIRONMENT)
    async with client_asaas:
        service = ChefDeliveryAsaasService(
            client_asaas, repository=get_payment_repository())
        if not st.session_state.get("current_order_id"):
            st.session_state["current_order_id"] = f"PED-{date.today().strftime('%Y%m%d')}-001"
        return await create_payment_from_streamlit_session(
            service,
            st.session_state,
            due_date=(date.today() + timedelta(days=1)).isoformat(),
            order_id=st.session_state["current_order_id"],
            total_value=st.session_state.get("total_value") or 0,
            payment_method=st.session_state.get("payment_method") or "pix",
            email=st.session_state.get("email") or None,
            cpf_cnpj=st.session_state.get("cpf_cnpj") or None,
            postal_code=st.session_state.get("postal_code") or None,
            address_number=st.session_state.get("address_number") or None,
            province=st.session_state.get("province") or None,
            remote_ip=st.session_state.get("remote_ip") or "127.0.0.1",
        )


def render_payment_panel() -> None:
    st.subheader("💳 Pagamento ASAAS")
    st.session_state["payment_method"] = st.selectbox(
        "Método de pagamento",
        ["pix", "boleto", "credit_card_checkout"],
        index=["pix", "boleto", "credit_card_checkout"].index(
            st.session_state.get("payment_method", "pix")),
    )

    ready, missing = order_is_ready_for_payment()
    if not ASAAS_API_KEY:
        st.error("ASAAS_API_KEY não configurada no ambiente.")
        return

    if not ready:
        st.info("Para gerar o pagamento ainda faltam: " + ", ".join(missing))
    else:
        st.success("Pedido pronto para gerar cobrança.")

    if st.button("Gerar cobrança agora", type="primary", use_container_width=True, disabled=not ready):
        try:
            st.session_state["payment_error"] = ""
            st.session_state["payment_result"] = asyncio.run(
                generate_order_payment())
            st.success("Cobrança gerada com sucesso.")
        except Exception as exc:
            st.session_state["payment_result"] = None
            st.session_state["payment_error"] = str(exc)

    if st.session_state.get("payment_error"):
        st.error(st.session_state["payment_error"])

    result = st.session_state.get("payment_result")
    if result:
        st.markdown("### Resultado do pagamento")
        st.json(result)
        if result.get("pix_payload"):
            st.code(result["pix_payload"], language="text")
        if result.get("pix_qr_code_base64"):
            st.image(f"data:image/png;base64,{result['pix_qr_code_base64']}")
        if result.get("invoice_url"):
            st.link_button("Abrir link de pagamento", result["invoice_url"])
        if result.get("bank_slip_url"):
            st.link_button("Abrir boleto", result["bank_slip_url"])


def load_test_example() -> None:
    st.session_state["name"] = "Maria Aparecida Souza"
    st.session_state["primeiro_nome"] = "Maria"
    st.session_state["whatsapp"] = "31988887777"
    st.session_state["email"] = "maria@example.com"
    st.session_state["cpf_cnpj"] = "12345678909"
    st.session_state["endereco"] = "Avenida Amazonas, 456 - Centro - Belo Horizonte/MG"
    st.session_state["postal_code"] = "30180000"
    st.session_state["address_number"] = "456"
    st.session_state["province"] = "Centro"
    st.session_state["pedido"] = ["2kg Bisteca", "1 Pão de Alho Shamara"]
    st.session_state["pedido_texto"] = "2kg Bisteca + 1 Pão de Alho Shamara"
    st.session_state["observacao"] = "Entregar no período da tarde"
    st.session_state["total_value"] = 43.97
    st.session_state["payment_method"] = "boleto"


def main() -> None:
    st.set_page_config(page_title="Chef Delivery Chat + ASAAS", layout="wide")
    inicializar_session_state()

    st.title("🥩 Chef Delivery")
    st.caption("Chat de pedido com geração de pagamento ASAAS no próprio fluxo.")

    if "messages" not in st.session_state:
        primeiro_nome = st.session_state.get("primeiro_nome") or "Cliente"
        st.session_state.messages = [
            {"role": "assistant", "content": f"Olá, {primeiro_nome}! Sou o Chef Delivery. Me diga o que você deseja comprar hoje."}]

    col_chat, col_side = st.columns([1.3, 1])

    with col_side:
        if st.button("Carregar teste: 2kg Bisteca + 1 Pão de Alho Shamara"):
            load_test_example()
            st.success("Exemplo de teste carregado.")
        render_order_capture_panel()
        render_payment_panel()

    with col_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Digite sua mensagem"):
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            parse_order_fields_from_text(prompt)
            reply = build_groq_response()
            st.session_state.messages.append(
                {"role": "assistant", "content": reply})
            st.rerun()


if __name__ == "__main__":
    main()
