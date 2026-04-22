import os
import uuid
import base64
import asyncio
from pathlib import Path
from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from api_asaas import (
    AsaasConfig,
    AsaasError,
    ChefDeliveryAsaasService,
    build_asaas_client,
    create_payment_from_streamlit_session,
)
from services.flow_manager import ChefDeliveryFlowManager

load_dotenv()


def _get_secret(path: str, default=None):
    try:
        value = st.secrets
        for part in path.split("."):
            value = value[part]
        return value
    except Exception:
        return default


def _resolve_groq_api_key() -> str:
    """Busca a chave GROQ em múltiplos locais possíveis (runtime).

    Ordem: variável de ambiente -> st.secrets em várias seções comuns.
    Avaliado em runtime para evitar problemas de import time no Streamlit Cloud.
    """
    env_value = os.getenv("GROQ_API_KEY", "")
    if env_value:
        return env_value
    candidates = [
        "GROQ_API_KEY",
        "groq.GROQ_API_KEY",
        "api_keys.GROQ_API_KEY",
        "default.GROQ_API_KEY",
    ]
    for path in candidates:
        value = _get_secret(path)
        if value:
            return str(value)
    return ""


def _resolve_asaas_api_key() -> str:
    env_value = os.getenv("ASAAS_API_KEY", "")
    if env_value:
        return env_value
    candidates = [
        "ASAAS_API_KEY",
        "asaas.ASAAS_API_KEY",
        "api_keys.ASAAS_API_KEY",
        "default.ASAAS_API_KEY",
    ]
    for path in candidates:
        value = _get_secret(path)
        if value:
            return str(value)
    return ""


def _resolve_asaas_environment() -> str:
    value = (
        os.getenv("ASAAS_ENVIRONMENT")
        or _get_secret("asaas.ASAAS_ENVIRONMENT")
        or _get_secret("ASAAS_ENVIRONMENT")
        or "sandbox"
    )
    return str(value).lower()


GROQ_API_KEY = _resolve_groq_api_key()
ASAAS_API_KEY = _resolve_asaas_api_key()
ASAAS_ENVIRONMENT = _resolve_asaas_environment()


@st.cache_resource(show_spinner=False)
def get_groq_client():
    key = GROQ_API_KEY or _resolve_groq_api_key()
    if not key:
        return None
    return Groq(api_key=key)


@st.cache_data(show_spinner=False)
def build_image_data_uri(relative_path: str) -> str:
    image_path = Path(__file__).resolve().parent.parent / relative_path
    if not image_path.exists():
        return ""
    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    suffix = image_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")
    return f"data:{mime_type};base64,{encoded}"


def inicializar_session_state():
    campos = [
        "name",
        "primeiro_nome",
        "endereco",
        "whatsapp",
        "pedido",
        "observacao",
        "total_value",
        "pedido_texto",
        "messages",
        "username",
        "email",
        "asaas_payment_result",
    ]
    for campo in campos:
        if campo not in st.session_state:
            if campo == "pedido":
                st.session_state[campo] = []
            elif campo == "total_value":
                st.session_state[campo] = 0.0
            elif campo == "messages":
                st.session_state[campo] = []
            elif campo == "asaas_payment_result":
                st.session_state[campo] = None
            else:
                st.session_state[campo] = ""


@st.cache_data(show_spinner=False)
def build_system_prompt(primeiro_nome: str) -> str:
    return f"""
Você é o Chef Delivery, especialista em vendas online de carnes, churrasco, bebidas e complementos.
Use o nome "{primeiro_nome}" para personalizar as mensagens.
Seja curto, claro e objetivo.
Sempre conduza o cliente até o fechamento do pedido.

Fluxo obrigatório:
1. Descobrir o que o cliente deseja.
2. Apresentar as opções em tópicos numerados.
3. Informar o preço do item escolhido.
4. Perguntar a quantidade.
5. Perguntar se deseja adicionar mais alguma coisa.
6. Ao final, pedir nome, endereço e WhatsApp.
7. Confirmar o total.
8. Informar que o pagamento PIX poderá ser gerado pelo sistema.

Regras:
- Não aceitar pedido de carne com menos de 1kg.
- Se houver produtos parecidos, pergunte qual exatamente o cliente quer.
- Mantenha respostas objetivas.
- O atendimento deve soar humano, cordial e comercial.
- Se o cliente já escolheu um produto, direcione para definir quantidade.
- Se o cliente quiser finalizar, oriente para confirmação do total e pagamento.

Alguns itens e preços:
- Picanha premiata custa R$ 79,99 por kg.
- Alcatra custa R$ 36,99 por kg.
- Contra filé custa R$ 37,99 por kg.
- Chã de dentro custa R$ 33,99 por kg.
- Patinho custa R$ 33,99 por kg.
- Fraldinha custa R$ 34,99 por kg.
- Costela de boi custa R$ 19,99 por kg.
- Coxa e sobrecoxa custam R$ 9,99 por kg.
- Peito de frango custa R$ 14,99 por kg.
- Linguiça toscana FM custa R$ 14,99 por kg.
- Linguiça caseira custa R$ 19,99 por kg.
- Bacon custa R$ 29,99 por kg.
- Po de alho Shamara custa R$ 9,99 por unidade.
- Carvão de 3kg custa R$ 14,99 por unidade.
- Coca-Cola lata 350ml custa R$ 4,99.
- Fanta lata 350ml custa R$ 4,99.
- Água 500ml custa R$ 3,00.

Kits:
- Kit Churrasco Diamante: R$ 229,99.
- Kit Churrasco Gold: R$ 169,99.
- Kit Churrasco Prata: R$ 149,99.
- Kit Bronze: R$ 99,99.
- Kit Economia: R$ 109,99.
"""


def clear_chat_history():
    primeiro_nome = (
        st.session_state.primeiro_nome
        if st.session_state.get("primeiro_nome")
        else "Cliente"
    )
    mensagem_inicial = (
        f"Olá, {primeiro_nome}! Sou o Chef Delivery, digite abaixo o que você deseja comprar hoje?"
    )

    preserve_keys = {
        "name": st.session_state.get("name", ""),
        "primeiro_nome": st.session_state.get("primeiro_nome", ""),
        "endereco": st.session_state.get("endereco", ""),
        "whatsapp": st.session_state.get("whatsapp", ""),
        "username": st.session_state.get("username", ""),
        "email": st.session_state.get("email", ""),
    }

    keys_to_clear = [
        "messages",
        "pedido",
        "observacao",
        "total_value",
        "pedido_texto",
        "flow_state",
        "cart",
        "current_group",
        "current_category",
        "current_product",
        "checkout_ready",
        "payment_data",
        "asaas_payment_result",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    for key, value in preserve_keys.items():
        st.session_state[key] = value

    st.session_state.messages = [
        {"role": "assistant", "content": mensagem_inicial}
    ]


def apply_chat_styles():
    st.markdown(
        """
        <style>
        .chat-bottom-actions {
            margin-top: 0.35rem;
            margin-bottom: 0.6rem;
        }
        .chat-credit-box {
            margin-top: 1rem;
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
            border: 1px solid rgba(122,240,176,0.14);
            color: #dbeafe;
            font-size: 0.94rem;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset, 0 10px 22px rgba(0,0,0,0.18);
        }
        .chat-credit-box a {
            color: #7af0b0 !important;
            text-decoration: none;
            font-weight: 700;
        }
        section[data-testid="stSidebar"] > div {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sync_order_state_from_cart():
    cart = st.session_state.get("cart", [])
    st.session_state.pedido = [
        f"{item['nome']} ({item['quantidade']} {item['unidade']})"
        for item in cart
    ]
    st.session_state.pedido_texto = ", ".join(st.session_state.pedido)
    st.session_state.total_value = round(
        sum(item["subtotal"] for item in cart), 2
    )


async def _create_pix_payment_async():
    if not ASAAS_API_KEY:
        raise AsaasError("ASAAS_API_KEY não configurada.")

    total_value = st.session_state.get("total_value", 0.0)
    if not total_value or total_value <= 0:
        raise AsaasError("O valor total do pedido está vazio ou inválido.")

    order_id = f"CHEF-{uuid.uuid4().hex[:10].upper()}"
    due_date = (date.today() + timedelta(days=1)).isoformat()

    client = await build_asaas_client(
        ASAAS_API_KEY,
        environment="production" if ASAAS_ENVIRONMENT == "production" else "sandbox",
    )

    async with client:
        service = ChefDeliveryAsaasService(client)
        result = await create_payment_from_streamlit_session(
            service,
            st.session_state,
            due_date=due_date,
            order_id=order_id,
            total_value=total_value,
            payment_method="pix",
            email=st.session_state.get("email") or None,
        )
        return result


def _render_pix_payment_block():
    payment_data = st.session_state.get("payment_data")
    flow_state = st.session_state.get("flow_state")

    if flow_state != "aguardando_pagamento":
        return

    if not payment_data or payment_data.get("billing_type") != "PIX":
        return

    _sync_order_state_from_cart()
    total = st.session_state.get("total_value", 0.0)

    st.markdown("### Pagamento PIX")
    st.write(f"Total do pedido: **R$ {total:.2f}**")

    if not ASAAS_API_KEY:
        st.error(
            "A chave ASAAS_API_KEY não foi encontrada. Verifique o .env ou o secrets.toml.")
        return

    if st.button("Gerar PIX", type="primary", use_container_width=True, key="gerar_pix_asaas"):
        try:
            result = asyncio.run(_create_pix_payment_async())
            st.session_state.asaas_payment_result = result
            st.session_state.flow_state = "pedido_finalizado"
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Seu PIX foi gerado com sucesso. Abaixo está o QR Code e o código copia e cola para pagamento."
                }
            )
            st.rerun()
        except AsaasError as e:
            st.error(f"Erro Asaas: {e}")
        except Exception as e:
            st.error(f"Erro inesperado ao gerar PIX: {e}")


def _render_payment_result():
    result = st.session_state.get("asaas_payment_result")
    if not result:
        return

    st.markdown("### PIX gerado")
    if result.get("value") is not None:
        st.write(f"Valor: **R$ {float(result['value']):.2f}**")

    if result.get("pix_qr_code_base64"):
        st.image(f"data:image/png;base64,{result['pix_qr_code_base64']}")

    if result.get("pix_payload"):
        st.caption("Código PIX copia e cola")
        st.code(result["pix_payload"], language="text")

    if result.get("pix_expiration_date"):
        st.caption(f"Expiração: {result['pix_expiration_date']}")

    if result.get("payment_id"):
        st.caption(f"Payment ID: {result['payment_id']}")


def showPedido():
    apply_chat_styles()
    inicializar_session_state()

    flow = ChefDeliveryFlowManager()
    flow.init_state()

    primeiro_nome = (
        st.session_state.primeiro_nome
        if st.session_state.get("primeiro_nome")
        else (
            st.session_state.name.split(" ")[0]
            if st.session_state.get("name")
            else "Cliente"
        )
    )

    if not st.session_state.messages:
        mensagem_inicial = (
            f"Olá, {primeiro_nome}! Sou o Chef Delivery, digite abaixo o que você deseja comprar hoje?"
        )
        st.session_state.messages = [
            {"role": "assistant", "content": mensagem_inicial}
        ]

    system_prompt = build_system_prompt(primeiro_nome)

    # Determina o avatar do usuário (foto de perfil ou imagem padrão)
    from database.services.profile_image_service import get_profile_image_path
    import os as _os
    
    user_profile_img = st.session_state.get("user_profile_image", "")
    user_avatar = "./src/img/cliente.png"
    
    if user_profile_img:
        profile_path = get_profile_image_path(user_profile_img)
        if profile_path and _os.path.exists(profile_path):
            user_avatar = profile_path
    
    # Verifica se a imagem padrão existe
    if not _os.path.exists(user_avatar):
        user_avatar = None  # Streamlit usará avatar padrão

    icons = {
        "assistant": "./src/img/perfil-chat1.png" if _os.path.exists("./src/img/perfil-chat1.png") else None,
        "user": user_avatar,
    }

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons.get(message["role"])):
            st.write(message["content"])

    flow.render_quantity_widget()
    flow.render_order_summary()
    _render_pix_payment_block()
    _render_payment_result()

    if not GROQ_API_KEY:
        # Re-tenta em runtime caso o secrets só tenha sido carregado depois do import
        runtime_key = _resolve_groq_api_key()
        if runtime_key:
            globals()["GROQ_API_KEY"] = runtime_key
            get_groq_client.clear()
        else:
            st.warning(
                "A chave GROQ_API_KEY não foi encontrada. Verifique o .env ou o secrets.toml."
            )

    client = get_groq_client()

    def generate_groq_response():
        if client is None:
            yield "No momento o chat está sem conexão com a IA. Verifique a configuração da GROQ_API_KEY."
            return

        messages = [{"role": "system", "content": system_prompt}]
        for dict_message in st.session_state.messages:
            messages.append(
                {
                    "role": dict_message["role"],
                    "content": dict_message["content"],
                }
            )

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=3500,
            top_p=1,
            stream=True,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    prompt = st.chat_input("Digite sua mensagem")

    if prompt:
        flow.handle_user_message(prompt)
        _sync_order_state_from_cart()
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar=icons["assistant"]):
            response = generate_groq_response()
            full_response = st.write_stream(response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    st.sidebar.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div class="chat-credit-box">
            Desenvolvido por
            <a href="https://portifolio-william-eustaquio.streamlit.app/" target="_blank">
                William Eustáquio
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
