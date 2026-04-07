import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import streamlit as st
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MCP_SERVER_PATH = Path(__file__).with_name("asaas_mcp_server.py")


def inicializar_state() -> None:
    defaults = {
        "name": "",
        "primeiro_nome": "",
        "endereco": "",
        "whatsapp": "",
        "pedido": [],
        "pedido_texto": "",
        "total_value": 0.0,
        "observacao": "",
        "email": "",
        "cpf_cnpj": "",
        "postal_code": "",
        "address_number": "",
        "province": "",
        "payment_method": "pix",
        "mcp_payment_result": None,
        "mcp_payment_error": "",
        "current_order_id": f"PED-CHAT-{date.today().strftime('%Y%m%d')}-001",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_system_prompt() -> str:
    return """
Você é o Chef Delivery.
Seu objetivo é ajudar o cliente a fechar um pedido e preparar os dados para pagamento.
Seja breve e claro.
Quando o pedido estiver fechado, oriente que o pagamento pode ser gerado no painel lateral.
Nunca invente preços; use somente os dados confirmados pelo operador.
"""


def call_groq() -> str:
    if not client:
        return "GROQ_API_KEY não configurada."
    messages = [{"role": "system", "content": build_system_prompt()}]
    messages.extend(st.session_state.messages)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=400,
    )
    return completion.choices[0].message.content


def parse_simple_fields(prompt: str) -> None:
    lower = prompt.lower().strip()
    if lower.startswith("nome:"):
        name = prompt.split(":", 1)[1].strip()
        st.session_state["name"] = name
        st.session_state["primeiro_nome"] = name.split()[0] if name else ""
    elif lower.startswith("endereço:") or lower.startswith("endereco:"):
        st.session_state["endereco"] = prompt.split(":", 1)[1].strip()
    elif lower.startswith("whatsapp:"):
        st.session_state["whatsapp"] = ''.join(
            ch for ch in prompt if ch.isdigit())
    elif lower.startswith("pedido:"):
        st.session_state["pedido_texto"] = prompt.split(":", 1)[1].strip()
    elif lower.startswith("total:"):
        raw = prompt.split(":", 1)[1].strip().replace(
            "R$", "").replace(",", ".")
        try:
            st.session_state["total_value"] = float(raw)
        except ValueError:
            pass
    elif lower.startswith("email:"):
        st.session_state["email"] = prompt.split(":", 1)[1].strip()
    elif lower.startswith("cpf:") or lower.startswith("cpf/cnpj:"):
        st.session_state["cpf_cnpj"] = ''.join(
            ch for ch in prompt if ch.isdigit())


def order_ready() -> tuple[bool, list[str]]:
    missing = []
    if not st.session_state.get("name"):
        missing.append("nome")
    if not st.session_state.get("endereco"):
        missing.append("endereço")
    if not st.session_state.get("whatsapp"):
        missing.append("WhatsApp")
    if not st.session_state.get("pedido_texto"):
        missing.append("pedido")
    if float(st.session_state.get("total_value") or 0) <= 0:
        missing.append("total")
    return (len(missing) == 0, missing)


def call_mcp_tool(tool: str, payload: dict) -> dict:
    if not MCP_SERVER_PATH.exists():
        return {"ok": False, "error": f"Servidor MCP não encontrado em {MCP_SERVER_PATH}"}

    process = subprocess.Popen(
        [sys.executable, str(MCP_SERVER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    message = json.dumps(
        {"tool": tool, "payload": payload}, ensure_ascii=False)
    stdout, stderr = process.communicate(message + "\n", timeout=60)
    if stderr and not stdout.strip():
        return {"ok": False, "error": stderr.strip()}
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        return {"ok": False, "error": "Sem resposta do servidor MCP"}
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"ok": False, "error": lines[-1]}


def render_side_panel() -> None:
    st.subheader("🧾 Pedido estruturado")
    st.session_state["name"] = st.text_input(
        "Nome", value=st.session_state.get("name", ""))
    st.session_state["endereco"] = st.text_area(
        "Endereço", value=st.session_state.get("endereco", ""), height=100)
    st.session_state["whatsapp"] = st.text_input(
        "WhatsApp", value=st.session_state.get("whatsapp", ""))
    st.session_state["pedido_texto"] = st.text_area(
        "Pedido", value=st.session_state.get("pedido_texto", ""), height=100)
    st.session_state["total_value"] = st.number_input("Total", min_value=0.0, step=0.01, value=float(
        st.session_state.get("total_value") or 0.0), format="%.2f")
    st.session_state["payment_method"] = st.selectbox("Pagamento", ["pix", "boleto", "credit_card_checkout"], index=[
                                                      "pix", "boleto", "credit_card_checkout"].index(st.session_state.get("payment_method", "pix")))
    st.session_state["email"] = st.text_input(
        "Email", value=st.session_state.get("email", ""))
    st.session_state["cpf_cnpj"] = st.text_input(
        "CPF/CNPJ", value=st.session_state.get("cpf_cnpj", ""))
    st.session_state["postal_code"] = st.text_input(
        "CEP", value=st.session_state.get("postal_code", ""))
    st.session_state["address_number"] = st.text_input(
        "Número", value=st.session_state.get("address_number", ""))
    st.session_state["province"] = st.text_input(
        "Bairro", value=st.session_state.get("province", ""))

    ready, missing = order_ready()
    if ready:
        st.success("Pedido pronto para enviar ao MCP.")
    else:
        st.info("Faltam: " + ", ".join(missing))

    if st.button("Gerar pagamento via MCP", type="primary", use_container_width=True, disabled=not ready):
        payload = {
            "order_id": st.session_state.get("current_order_id"),
            "name": st.session_state.get("name"),
            "endereco": st.session_state.get("endereco"),
            "whatsapp": st.session_state.get("whatsapp"),
            "pedido_texto": st.session_state.get("pedido_texto"),
            "pedido": st.session_state.get("pedido") or [],
            "total_value": st.session_state.get("total_value"),
            "payment_method": st.session_state.get("payment_method"),
            "observacao": st.session_state.get("observacao"),
            "email": st.session_state.get("email"),
            "cpf_cnpj": st.session_state.get("cpf_cnpj"),
            "postal_code": st.session_state.get("postal_code"),
            "address_number": st.session_state.get("address_number"),
            "province": st.session_state.get("province"),
        }
        response = call_mcp_tool("create_order_payment", payload)
        if response.get("ok"):
            st.session_state["mcp_payment_result"] = response.get("data")
            st.session_state["mcp_payment_error"] = ""
            st.success("Pagamento gerado via MCP.")
        else:
            st.session_state["mcp_payment_result"] = None
            st.session_state["mcp_payment_error"] = response.get(
                "error", "Erro desconhecido")

    if st.button("Consultar exemplos MCP"):
        response = call_mcp_tool("list_test_order_examples", {})
        if response.get("ok"):
            st.json(response.get("data"))
        else:
            st.error(response.get("error", "Erro ao consultar exemplos"))

    if st.session_state.get("mcp_payment_error"):
        st.error(st.session_state["mcp_payment_error"])

    if st.session_state.get("mcp_payment_result"):
        result = st.session_state["mcp_payment_result"]
        st.markdown("### Retorno MCP")
        st.json(result)
        if result.get("pix_payload"):
            st.code(result["pix_payload"], language="text")
        if result.get("invoice_url"):
            st.link_button("Abrir link de pagamento", result["invoice_url"])
        if result.get("bank_slip_url"):
            st.link_button("Abrir boleto", result["bank_slip_url"])


def load_test_mcp_example() -> None:
    st.session_state["name"] = "João Pedro Silva"
    st.session_state["primeiro_nome"] = "João"
    st.session_state["endereco"] = "Rua das Acácias, 123 - Centro - Belo Horizonte/MG"
    st.session_state["whatsapp"] = "31999991111"
    st.session_state["pedido_texto"] = "1 Kit Gold + 2 Coca Zero 600ml"
    st.session_state["pedido"] = ["Kit Gold", "Coca Zero 600ml x2"]
    st.session_state["total_value"] = 163.97
    st.session_state["payment_method"] = "pix"
    st.session_state["email"] = "joao@example.com"
    st.session_state["cpf_cnpj"] = "12345678909"
    st.session_state["postal_code"] = "30110000"
    st.session_state["address_number"] = "123"
    st.session_state["province"] = "Centro"


def main() -> None:
    st.set_page_config(page_title="Chef Delivery Chat MCP", layout="wide")
    inicializar_state()

    st.title("🥩 Chef Delivery + MCP")
    st.caption("Chat do pedido com geração de pagamento via servidor MCP.")

    if "messages" not in st.session_state:
        primeiro_nome = st.session_state.get("primeiro_nome") or "Cliente"
        st.session_state.messages = [
            {"role": "assistant", "content": f"Olá, {primeiro_nome}! Me diga o que você quer pedir hoje."}]

    col_chat, col_side = st.columns([1.3, 1])

    with col_side:
        if st.button("Carregar teste MCP: Kit Gold + 2 Coca Zero 600ml"):
            load_test_mcp_example()
            st.success("Teste carregado.")
        render_side_panel()

    with col_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Digite uma mensagem ou preencha usando campos como Nome:, Endereço:, Pedido:, Total:"):
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            parse_simple_fields(prompt)
            answer = call_groq()
            st.session_state.messages.append(
                {"role": "assistant", "content": answer})
            st.rerun()


if __name__ == "__main__":
    main()
