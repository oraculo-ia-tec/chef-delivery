import base64
import os
from datetime import date
from pathlib import Path

import streamlit as st
from groq import Groq

from chef_order_flow_sqlite import ChefOrderFlowRepository
from pgs.produtos import CATEGORIAS, KITS_DESCRICAO

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
repo = ChefOrderFlowRepository()


@st.cache_resource(show_spinner=False)
def get_groq_client():
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


@st.cache_data(show_spinner=False)
def _file_to_data_uri(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        return ""
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{encoded}"


@st.cache_data(show_spinner=False)
def _build_local_image_data_uri(relative_path: str) -> str:
    image_path = Path(__file__).resolve().parent.parent / relative_path
    return _file_to_data_uri(str(image_path))


def build_user_profile_image_uri() -> str:
    email = (st.session_state.get("username") or "").strip().lower()
    if not email:
        return ""

    base_dir = Path(__file__).resolve().parent.parent / \
        "src" / "img" / "profiles"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        image_path = base_dir / f"{email}{ext}"
        if image_path.exists():
            return _file_to_data_uri(str(image_path))
    return ""


def get_avatar(role: str) -> str | None:
    if role == "assistant":
        return _build_local_image_data_uri("src/img/perfil.png") or None
    if role == "user":
        return build_user_profile_image_uri() or None
    return None


def _default_order_id() -> str:
    return f"PED-CHAT-{date.today().strftime('%Y%m%d')}-001"


def inicializar_session_state() -> None:
    defaults = {
        "messages": [],
        "order_id": _default_order_id(),
        "customer_name": st.session_state.get("name", ""),
        "customer_address": "",
        "customer_whatsapp": "",
        "observacao": "",
        "checkout_ready": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state["messages"]:
        primeira_msg = (
            "Qual categoria você quer ver primeiro? "
            "Temos Boi, Porco, Frango, Linguiça / Embutidos, Peixe, Kits Churrasco, Bebidas e Acompanhamentos."
        )
        st.session_state["messages"] = [
            {"role": "assistant", "content": primeira_msg}]


def inject_pedido_hero_style() -> None:
    st.markdown(
        """
        <style>
        .pedido-chat-wrap {max-width: 920px; margin: 0 auto;}
        .pedido-hero-wrap {display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; margin:0 auto 1.2rem auto; padding:0.2rem 0 0.8rem 0;}
        .pedido-hero-image {width:138px; height:138px; border-radius:50%; object-fit:cover; border:3px solid rgba(120,255,182,0.30); box-shadow:0 0 18px rgba(0,255,170,0.18); animation:pedidoChefPulse 2.4s linear infinite, pedidoChefFloat 3s linear infinite; transform-origin:center; margin-bottom:0.85rem;}
        .pedido-hero-title {font-size:2.6rem; font-weight:800; line-height:1.06; margin-bottom:0.45rem; color:#ffffff;}
        .pedido-hero-subtitle {max-width:780px; font-size:1.02rem; line-height:1.65; color:#cfd8e7; margin:0 auto;}
        .pedido-summary-box {padding:1rem 1.1rem; border-radius:16px; background:rgba(255,255,255,0.04); border:1px solid rgba(120,255,182,0.10); margin:1rem auto 1.1rem auto;}
        .pedido-summary-title {font-size:1.05rem; font-weight:700; margin-bottom:0.5rem; color:#ffffff;}
        .pedido-summary-text {color:#d5dfec; line-height:1.65; white-space:pre-wrap;}
        .pedido-inline-action {margin-top:0.85rem;}
        div[data-testid="stChatMessageAvatarUser"] img, div[data-testid="stChatMessageAvatarAssistant"] img {object-fit:cover !important; border-radius:50% !important;}
        @keyframes pedidoChefPulse {0%,100%{transform:scale(1); box-shadow:0 0 14px rgba(0,255,170,0.12);} 50%{transform:scale(1.10); box-shadow:0 0 28px rgba(0,255,170,0.24);}}
        @keyframes pedidoChefFloat {0%,100%{transform:translateY(0px);} 50%{transform:translateY(-10px);}}
        @media (max-width: 768px) {.pedido-hero-image {width:112px; height:112px;} .pedido-hero-title {font-size:2rem;} .pedido-hero-subtitle {font-size:0.96rem; max-width:100%; padding:0 0.4rem;} .pedido-chat-wrap {max-width:100%;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pedido_hero() -> None:
    primeiro_nome = st.session_state.get("primeiro_nome", "") or "Cliente"
    image_uri = _build_local_image_data_uri("src/img/perfil.png")
    st.markdown(
        f"""
        <div class="pedido-hero-wrap">
            <img class="pedido-hero-image" src="{image_uri}" alt="Chef Delivery">
            <div class="pedido-hero-title">Chef Delivery</div>
            <div class="pedido-hero-subtitle">Olá, {primeiro_nome}! Sou o Chef Delivery. Vou te ajudar a escolher seus produtos, montar seu pedido e seguir até a finalização.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_system_prompt() -> str:
    return "\n".join([
        "Você é o Chef Delivery, um assistente comercial de vendas para açougue e churrasco.",
        "Seja breve, claro e comercial.",
        "Apresente categorias, produtos, preços e sugestões somente com base no catálogo disponível.",
        "Nunca invente preços, produtos, promoções ou disponibilidade fora do catálogo.",
        "Se o cliente demonstrar intenção de compra, conduza de forma objetiva para escolher categoria, produto e quantidade.",
        "Se houver itens no pedido, use o resumo atual para continuar a conversa.",
    ])


def normalize_text(text: str) -> str:
    return (text.lower().replace("ç", "c").replace("ã", "a").replace("á", "a").replace("à", "a").replace("â", "a").replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("õ", "o").replace("ú", "u"))


def find_category_from_message(message: str) -> str | None:
    text = normalize_text(message)
    category_map = {
        "boi": "🥩 Boi",
        "carne bovina": "🥩 Boi",
        "bovino": "🥩 Boi",
        "porco": "🐷 Porco",
        "suino": "🐷 Porco",
        "frango": "🍗 Frango",
        "linguica": "🌭 Linguiça / Embutidos",
        "embutidos": "🌭 Linguiça / Embutidos",
        "peixe": "🐟 Peixe",
        "kits": "🔥 Kits Churrasco",
        "kit churrasco": "🔥 Kits Churrasco",
        "bebida": "🥤 Bebidas",
        "bebidas": "🥤 Bebidas",
        "acompanhamento": "🧂 Acompanhamentos",
        "acompanhamentos": "🧂 Acompanhamentos",
    }
    for termo, categoria in category_map.items():
        if termo in text:
            return categoria
    return None


def build_categories_text() -> str:
    return "\n".join([f"- {categoria}" for categoria in CATEGORIAS.keys()])


def build_products_text(category: str) -> str:
    itens = sorted(CATEGORIAS[category]["itens"].items(),
                   key=lambda item: item[0].lower())
    unidade = CATEGORIAS[category]["unidade"]
    linhas = [f"Produtos da categoria {category}:"]
    for nome, preco in itens:
        extra = f" — {KITS_DESCRICAO[nome]}" if category == "🔥 Kits Churrasco" and nome in KITS_DESCRICAO else ""
        linhas.append(f"- {nome}: R$ {float(preco):.2f}/{unidade}{extra}")
    return "\n".join(linhas)


def build_order_context(order_data: dict | None) -> str:
    if not order_data or not order_data.get("items"):
        return "Sem itens no pedido."
    linhas = ["Pedido atual:"]
    for item in order_data["items"]:
        linhas.append(
            f"- {item['product_name']} | {item['quantity']} {item['unit_type']} | subtotal R$ {float(item['subtotal']):.2f}")
    linhas.append(f"Total atual: R$ {float(order_data['total_value']):.2f}")
    return "\n".join(linhas)


def build_order_summary(order_data: dict | None) -> str:
    if not order_data or not order_data.get("items"):
        return "Nenhum item salvo ainda."
    lines = ["Resumo do pedido:"]
    for item in order_data["items"]:
        lines.append(
            f"- {item['product_name']}: {item['quantity']} {item['unit_type']} x R$ {float(item['unit_price']):.2f} = R$ {float(item['subtotal']):.2f}")
    lines.append(
        f"Total atual: R$ {float(order_data.get('total_value', 0)):.2f}")
    return "\n".join(lines)


def fallback_response(user_message: str, order_data: dict | None = None) -> str:
    categoria = find_category_from_message(user_message)
    texto = normalize_text(user_message)
    if any(palavra in texto for palavra in ["categoria", "menu", "opcoes", "opções", "produtos", "tipos"]):
        return "Estas são as categorias disponíveis:\n" + build_categories_text()
    if categoria:
        return build_products_text(categoria)
    if order_data and order_data.get("items") and any(p in texto for p in ["resumo", "pedido", "total", "carrinho"]):
        return build_order_summary(order_data)
    return "Posso te ajudar com as categorias e produtos do Chef Delivery. Digite a categoria que deseja ver, por exemplo: Boi, Porco, Frango, Peixe, Kits Churrasco, Bebidas ou Acompanhamentos."


def generate_llm_response(user_message: str, order_data: dict | None = None) -> str:
    client = get_groq_client()
    if client is None:
        return fallback_response(user_message, order_data)
    prompt = "\n\n".join([
        build_system_prompt(),
        "Categorias disponíveis:",
        build_categories_text(),
        "Contexto atual do pedido:",
        build_order_context(order_data),
        "Mensagem do cliente:",
        user_message,
    ])
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=260,
        )
        content = response.choices[0].message.content
        return content if content else fallback_response(user_message, order_data)
    except Exception:
        return fallback_response(user_message, order_data)


def clear_chat_history() -> None:
    primeira_msg = (
        "Qual categoria você quer ver primeiro? "
        "Temos Boi, Porco, Frango, Linguiça / Embutidos, Peixe, Kits Churrasco, Bebidas e Acompanhamentos."
    )
    st.session_state["messages"] = [
        {"role": "assistant", "content": primeira_msg}]
    st.session_state["order_id"] = _default_order_id()
    st.session_state["checkout_ready"] = False


def render_order_summary_box() -> None:
    order_data = repo.get_order(st.session_state["order_id"])
    resumo = build_order_summary(order_data)
    st.markdown(
        f"<div class='pedido-summary-box'><div class='pedido-summary-title'>Pedido atual</div><div class='pedido-summary-text'>{resumo}</div></div>", unsafe_allow_html=True)


def showPedido() -> None:
    inicializar_session_state()
    inject_pedido_hero_style()

    st.markdown('<div class="pedido-chat-wrap">', unsafe_allow_html=True)
    render_pedido_hero()
    render_order_summary_box()

    for idx, message in enumerate(st.session_state["messages"]):
        avatar = get_avatar(message["role"])
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    prompt = st.chat_input(
        "Digite a categoria ou o produto que deseja comprar")
    if prompt:
        st.session_state["messages"].append(
            {"role": "user", "content": prompt})
        order_data = repo.get_order(st.session_state["order_id"])
        answer = generate_llm_response(prompt, order_data)
        st.session_state["messages"].append(
            {"role": "assistant", "content": answer})
        st.rerun()

    st.markdown('<div class="pedido-inline-action">', unsafe_allow_html=True)
    if st.button("LIMPAR CONVERSA", use_container_width=True, key="pedido_limpar_conversa"):
        clear_chat_history()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
