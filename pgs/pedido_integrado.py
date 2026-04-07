import asyncio
import os
from datetime import date, timedelta
from typing import Any

import streamlit as st

from api_asaas import (
    ChefDeliveryAsaasService,
    InMemoryPaymentRepository,
    build_asaas_client,
    create_payment_from_streamlit_session,
)


ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_ENVIRONMENT = os.getenv("ASAAS_ENVIRONMENT", "sandbox")


@st.cache_resource(show_spinner=False)
def get_payment_repository() -> InMemoryPaymentRepository:
    return InMemoryPaymentRepository()


def ensure_payment_state() -> None:
    defaults = {
        "payment_result": None,
        "payment_error": "",
        "payment_method": "pix",
        "email": "",
        "cpf_cnpj": "",
        "postal_code": "",
        "address_number": "",
        "province": "",
        "remote_ip": "127.0.0.1",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def order_is_ready_for_payment(session_state: Any) -> tuple[bool, list[str]]:
    missing = []
    if not session_state.get("name"):
        missing.append("nome do cliente")
    if not session_state.get("endereco"):
        missing.append("endereço")
    if not session_state.get("whatsapp"):
        missing.append("WhatsApp")
    if not session_state.get("pedido_texto") and not session_state.get("pedido"):
        missing.append("descrição do pedido")
    total = float(session_state.get("total_value") or 0)
    if total <= 0:
        missing.append("total do pedido")
    return (len(missing) == 0, missing)


def build_payment_description(session_state: Any) -> str:
    description = session_state.get("pedido_texto")
    if description:
        return str(description)
    pedido = session_state.get("pedido") or []
    if isinstance(pedido, list):
        return ", ".join(map(str, pedido))
    return str(pedido or "Pedido Chef Delivery")


async def generate_order_payment() -> dict[str, Any]:
    client = await build_asaas_client(
        api_key=ASAAS_API_KEY,
        environment=ASAAS_ENVIRONMENT,
    )
    async with client:
        service = ChefDeliveryAsaasService(client, repository=get_payment_repository())
        order_id = st.session_state.get("current_order_id") or f"PED-{date.today().strftime('%Y%m%d')}-001"
        st.session_state["current_order_id"] = order_id
        due_date = (date.today() + timedelta(days=1)).isoformat()
        return await create_payment_from_streamlit_session(
            service,
            st.session_state,
            due_date=due_date,
            order_id=order_id,
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
    ensure_payment_state()

    st.subheader("💳 Finalização e Pagamento")
    st.caption("Gere a cobrança ASAAS ao finalizar o pedido do cliente.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["payment_method"] = st.selectbox(
            "Método de pagamento",
            options=["pix", "boleto", "credit_card_checkout"],
            index=["pix", "boleto", "credit_card_checkout"].index(st.session_state.get("payment_method", "pix")),
        )
        st.session_state["email"] = st.text_input("E-mail do cliente", value=st.session_state.get("email", ""))
        st.session_state["cpf_cnpj"] = st.text_input("CPF/CNPJ", value=st.session_state.get("cpf_cnpj", ""))

    with col2:
        st.session_state["postal_code"] = st.text_input("CEP", value=st.session_state.get("postal_code", ""))
        st.session_state["address_number"] = st.text_input("Número", value=st.session_state.get("address_number", ""))
        st.session_state["province"] = st.text_input("Bairro", value=st.session_state.get("province", ""))

    with st.expander("Resumo do pedido para pagamento", expanded=True):
        st.write({
            "cliente": st.session_state.get("name"),
            "endereco": st.session_state.get("endereco"),
            "whatsapp": st.session_state.get("whatsapp"),
            "descricao": build_payment_description(st.session_state),
            "total": st.session_state.get("total_value"),
            "metodo": st.session_state.get("payment_method"),
        })

    ready, missing = order_is_ready_for_payment(st.session_state)
    if not ASAAS_API_KEY:
        st.error("ASAAS_API_KEY não configurada no ambiente.")
        return

    if not ready:
        st.warning("Preencha os dados obrigatórios antes de gerar o pagamento: " + ", ".join(missing))
        return

    if st.button("Gerar cobrança ASAAS", type="primary", use_container_width=True):
        try:
            st.session_state["payment_error"] = ""
            result = asyncio.run(generate_order_payment())
            st.session_state["payment_result"] = result
            st.success("Cobrança gerada com sucesso.")
        except Exception as exc:
            st.session_state["payment_result"] = None
            st.session_state["payment_error"] = str(exc)

    if st.session_state.get("payment_error"):
        st.error(st.session_state["payment_error"])

    payment_result = st.session_state.get("payment_result")
    if payment_result:
        st.markdown("### Retorno do pagamento")
        st.json(payment_result)

        if payment_result.get("payment_method") == "pix":
            if payment_result.get("pix_payload"):
                st.code(payment_result["pix_payload"], language="text")
            if payment_result.get("pix_qr_code_base64"):
                st.image(f"data:image/png;base64,{payment_result['pix_qr_code_base64']}")

        if payment_result.get("invoice_url"):
            st.link_button("Abrir link de pagamento", payment_result["invoice_url"])

        if payment_result.get("bank_slip_url"):
            st.link_button("Abrir boleto", payment_result["bank_slip_url"])


def load_test_order_example_pix() -> None:
    st.session_state["name"] = "João Pedro Silva"
    st.session_state["primeiro_nome"] = "João"
    st.session_state["endereco"] = "Rua das Acácias, 123 - Centro - Belo Horizonte/MG"
    st.session_state["whatsapp"] = "31999991111"
    st.session_state["pedido"] = ["Kit Gold", "Coca Zero 600ml x2"]
    st.session_state["pedido_texto"] = "1 Kit Gold + 2 Coca Zero 600ml"
    st.session_state["total_value"] = 163.97
    st.session_state["payment_method"] = "pix"
    st.session_state["postal_code"] = "30110000"
    st.session_state["address_number"] = "123"
    st.session_state["province"] = "Centro"
    st.session_state["email"] = "joao@example.com"
    st.session_state["cpf_cnpj"] = "12345678909"


def render_test_buttons() -> None:
    st.markdown("### Cenário rápido de teste")
    if st.button("Carregar teste PIX: Kit Gold + 2 Coca Zero 600ml"):
        load_test_order_example_pix()
        st.success("Cenário de teste carregado.")


if __name__ == "__main__":
    st.set_page_config(page_title="Pedido Integrado ASAAS", layout="wide")
    st.title("Chef Delivery - Pedido com Pagamento ASAAS")
    render_test_buttons()
    render_payment_panel()