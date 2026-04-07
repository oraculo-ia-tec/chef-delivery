from __future__ import annotations

import os
from datetime import date

import streamlit as st
from groq import Groq

from chef_order_flow_sqlite import ChefOrderFlowRepository

CATEGORIAS = {
    "🥩 Boi": {"unidade": "kg", "itens": {"Alcatra (kg)": 36.99, "Contra filé (kg)": 37.99, "Picanha Premiata": 79.99, "Acém": 24.99, "Costela de boi": 19.99}},
    "🐷 Porco": {"unidade": "kg", "itens": {"Bisteca": 16.99, "Tomahawk suíno": 21.99, "Pernil": 18.99, "Lombo": 19.99, "Copa lombo": 21.99}},
    "🍗 Frango": {"unidade": "kg", "itens": {"Frango resfriado": 10.99, "Coxa e sobrecoxa": 9.99, "Peito de frango": 14.99, "Asa de frango": 14.99}},
    "🌭 Linguiça / Embutidos": {"unidade": "kg", "itens": {"Linguiça toscana FM": 14.99, "Linguiça defumada": 19.99, "Calabresa": 22.99, "Salsichão": 13.99}},
    "🐟 Peixe": {"unidade": "kg", "itens": {"Cavalinha": 10.99, "Sardinha": 14.99, "Filé de Merluza": 39.99, "Filé de Tilápia": 49.99}},
    "🔥 Kits Churrasco": {"unidade": "un", "itens": {"Kit Diamante": 229.99, "Kit Gold+": 169.99, "Kit Gold": 149.99, "Kit Bronze": 99.99}},
    "🥤 Bebidas": {"unidade": "un", "itens": {"Fanta PET 200ml": 2.99, "Coca-Cola PET 200ml": 2.99, "Coca Zero 600ml": 6.99, "Água s/ gás 500ml": 3.00}},
    "🧂 Acompanhamentos": {"unidade": "un", "itens": {"Pão de Alho Shamara": 9.99, "Pão de Alho Zé do Espeto": 21.99, "Carvão 3kg": 14.99, "Sal grosso": 2.99}},
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
repo = ChefOrderFlowRepository()


def init_state() -> None:
    defaults = {
        "messages": [],
        "order_id": f"PED-FLOW-{date.today().strftime('%Y%m%d')}-001",
        "selected_category": "🥩 Boi",
        "selected_product": None,
        "selected_unit": "kg",
        "selected_quantity": 1.0,
        "last_saved_order": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state["messages"]:
        st.session_state["messages"] = [{
            "role": "assistant",
            "content": "Olá! Estas são as categorias disponíveis: 🥩 Boi, 🐷 Porco, 🍗 Frango, 🌭 Linguiça / Embutidos, 🐟 Peixe, 🔥 Kits Churrasco, 🥤 Bebidas e 🧂 Acompanhamentos. Qual categoria você quer ver primeiro?"
        }]


def call_llm_summary(order_data: dict) -> str:
    if not client:
        return build_summary_text(order_data)
    items_text = "\n".join(
        f"- {item['product_name']} | {item['quantity']} {item['unit_type']} | unitário R$ {item['unit_price']:.2f} | subtotal R$ {item['subtotal']:.2f}"
        for item in order_data.get("items", [])
    )
    prompt = f"""
    Você é o Chef Delivery. Gere um resumo curto e objetivo da compra com base APENAS nos dados abaixo.
    Apresente os itens comprados e o total final. Termine perguntando se o cliente deseja mais algum produto.

    Pedido: {order_data.get('order_id')}
    Itens:
    {items_text}
    Total: R$ {float(order_data.get('total_value', 0)):.2f}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=250,
    )
    return response.choices[0].message.content


def build_summary_text(order_data: dict) -> str:
    lines = []
    for item in order_data.get("items", []):
        lines.append(
            f"- {item['product_name']}: {item['quantity']} {item['unit_type']} x R$ {item['unit_price']:.2f} = R$ {item['subtotal']:.2f}")
    return "Resumo da sua compra:\n" + "\n".join(lines) + f"\nTotal: R$ {float(order_data.get('total_value', 0)):.2f}\nDeseja adicionar mais algum produto?"


def show_category_products(category: str) -> None:
    data = CATEGORIAS[category]
    st.markdown("### Produtos da categoria")
    for name, price in data["itens"].items():
        st.write(f"- {name} — R$ {price:.2f}/{data['unidade']}")


def main() -> None:
    st.set_page_config(page_title="Chef Delivery Fluxo Correto", layout="wide")
    init_state()

    st.title("🥩 Chef Delivery - Fluxo Correto")
    st.caption(
        "Categorias primeiro, produtos depois, seleção visual e persistência item a item.")

    col_chat, col_ui = st.columns([1.1, 1])

    with col_chat:
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Digite a categoria desejada ou peça para ver as carnes"):
            st.session_state["messages"].append(
                {"role": "user", "content": prompt})
            lower = prompt.lower()
            if "carne" in lower or "categor" in lower or "tipos" in lower:
                answer = "Hoje trabalhamos com estas categorias: 🥩 Boi, 🐷 Porco, 🍗 Frango, 🌭 Linguiça / Embutidos, 🐟 Peixe, 🔥 Kits Churrasco, 🥤 Bebidas e 🧂 Acompanhamentos. Qual categoria você quer ver primeiro?"
            else:
                answer = "Escolha uma categoria no painel ao lado para ver os produtos e montar seu pedido."
            st.session_state["messages"].append(
                {"role": "assistant", "content": answer})
            st.rerun()

    with col_ui:
        st.subheader("1. Escolha a categoria")
        category = st.selectbox("Categorias", list(CATEGORIAS.keys()), index=list(
            CATEGORIAS.keys()).index(st.session_state["selected_category"]))
        st.session_state["selected_category"] = category
        show_category_products(category)

        products = list(CATEGORIAS[category]["itens"].keys())
        selected_product = st.selectbox("2. Escolha o produto", products)
        st.session_state["selected_product"] = selected_product

        default_unit = CATEGORIAS[category]["unidade"]
        unit_options = [default_unit] if default_unit == "kg" else ["un"]
        selected_unit = st.segmented_control(
            "3. Medida", options=unit_options, default=unit_options[0], selection_mode="single")
        quantity = st.number_input(
            "4. Quantidade",
            min_value=1.0,
            step=0.5 if selected_unit == "kg" else 1.0,
            value=1.0,
            format="%.1f" if selected_unit == "kg" else "%.0f",
        )

        unit_price = CATEGORIAS[category]["itens"][selected_product]
        subtotal = round(float(quantity) * float(unit_price), 2)
        st.metric("Subtotal do item", f"R$ {subtotal:.2f}")

        if st.button("5. Confirmar item e salvar no banco", type="primary", use_container_width=True):
            saved = repo.add_item(
                order_id=st.session_state["order_id"],
                category=category,
                product_name=selected_product,
                unit_type=selected_unit,
                quantity=float(quantity),
                unit_price=float(unit_price),
            )
            st.session_state["last_saved_order"] = saved
            resumo = call_llm_summary(
                repo.get_order(st.session_state["order_id"]))
            st.session_state["messages"].append(
                {"role": "assistant", "content": resumo})
            st.success("Item salvo no banco e resumo atualizado pelo LLM.")
            st.rerun()

        order_data = repo.get_order(st.session_state["order_id"])
        st.markdown("### 6. Pedido atual no banco")
        if order_data and order_data.get("items"):
            for item in order_data["items"]:
                st.write(
                    f"- {item['product_name']} | {item['quantity']} {item['unit_type']} | R$ {item['subtotal']:.2f}")
            st.metric("Total acumulado",
                      f"R$ {float(order_data['total_value']):.2f}")
        else:
            st.info("Nenhum item salvo ainda.")


if __name__ == "__main__":
    main()
