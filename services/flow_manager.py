from typing import Dict, Optional

import streamlit as st

from services.catalog_service import CatalogService
from services.order_service import OrderService


class ChefDeliveryFlowManager:
    def __init__(self):
        self.catalog = CatalogService()
        self.order = OrderService()

    def init_state(self):
        st.session_state.setdefault("flow_state", "aguardando_intencao")
        st.session_state.setdefault("cart", [])
        st.session_state.setdefault("current_group", None)
        st.session_state.setdefault("current_category", None)
        st.session_state.setdefault("current_product", None)
        st.session_state.setdefault("checkout_ready", False)
        st.session_state.setdefault("payment_data", None)

    def assistant_message(self, content: str):
        st.session_state.messages.append(
            {"role": "assistant", "content": content})

    def handle_user_message(self, text: str):
        text = text.strip()
        if not text:
            return

        st.session_state.messages.append({"role": "user", "content": text})

        flow_state = st.session_state.flow_state
        lowered = text.lower().strip()

        if flow_state == "aguardando_intencao":
            self._handle_initial_intent(lowered)
            return

        if flow_state == "aguardando_categoria":
            self._handle_category_choice(lowered)
            return

        if flow_state == "aguardando_modelo":
            self._handle_model_choice(text)
            return

        if flow_state == "aguardando_adicional":
            self._handle_additional_choice(lowered)
            return

        if flow_state == "aguardando_confirmacao_total":
            self._handle_total_confirmation(lowered)
            return

        if flow_state == "aguardando_pagamento":
            self._handle_payment_choice(lowered)
            return

        self.assistant_message(
            "Não entendi sua última resposta. Pode me informar o produto ou se deseja finalizar o pedido?")

    def _handle_initial_intent(self, lowered: str):
        result = self.catalog.find_group_or_category_from_text(lowered)
        product = self.catalog.find_product_from_text(lowered)

        if product:
            st.session_state.current_product = product
            st.session_state.flow_state = "aguardando_quantidade"
            self.assistant_message(
                f"Perfeito. Você escolheu **{product['nome']}**. Agora informe a quantidade no seletor abaixo."
            )
            return

        if result["group"] == "carnes" and result["category"] is None:
            st.session_state.current_group = "carnes"
            st.session_state.flow_state = "aguardando_categoria"
            categories = self.catalog.list_meat_categories()
            self.assistant_message(
                "Perfeito. Temos estas categorias de carne:\n\n" +
                "\n".join([f"{i+1}. {cat}" for i,
                          cat in enumerate(categories)])
            )
            return

        if result["group"] == "bebidas" and result["category"] is None:
            st.session_state.current_group = "bebidas"
            st.session_state.flow_state = "aguardando_categoria"
            categories = self.catalog.list_drink_categories()
            self.assistant_message(
                "Ótimo. Temos estas categorias de bebidas:\n\n" +
                "\n".join([f"{i+1}. {cat}" for i,
                          cat in enumerate(categories)])
            )
            return

        if result["category"]:
            st.session_state.current_group = result["group"]
            st.session_state.current_category = result["category"]
            st.session_state.flow_state = "aguardando_modelo"
            self._send_models_for_current_category()
            return

        self.assistant_message(
            "Posso te ajudar com **carnes** ou **bebidas**. Se quiser, me diga por exemplo: **quero picanha**, **quero peixe** ou **quero bebida**."
        )

    def _handle_category_choice(self, lowered: str):
        group = st.session_state.current_group

        if group == "carnes":
            valid = {c.lower(): c.lower()
                     for c in self.catalog.list_meat_categories()}
        else:
            valid = {c.lower(): c.lower()
                     for c in self.catalog.list_drink_categories()}

        selected = None
        for item in valid:
            if item in lowered:
                selected = item
                break

        if not selected:
            self.assistant_message(
                "Não identifiquei a categoria. Escolha uma das opções listadas acima.")
            return

        st.session_state.current_category = selected
        st.session_state.flow_state = "aguardando_modelo"
        self._send_models_for_current_category()

    def _send_models_for_current_category(self):
        group = st.session_state.current_group
        category = st.session_state.current_category
        models = self.catalog.get_models_by_category(group, category)

        if not models:
            self.assistant_message(
                "Não encontrei modelos para essa categoria no momento.")
            st.session_state.flow_state = "aguardando_intencao"
            return

        title = category.title()
        lines = [f"{i+1}. {model['nome']} — R$ {model['preco']:.2f}/{model['unidade']}" for i,
                 model in enumerate(models)]
        self.assistant_message(
            f"Estes são os modelos disponíveis de **{title}**:\n\n" + "\n".join(
                lines) + "\n\nDigite exatamente o modelo desejado."
        )

    def _handle_model_choice(self, text: str):
        product = self.catalog.find_product_by_name(text.strip())
        if not product:
            product = self.catalog.find_product_from_text(text)

        if not product:
            self.assistant_message(
                "Não identifiquei o modelo escolhido. Digite o nome do modelo conforme listado.")
            return

        st.session_state.current_product = product
        st.session_state.flow_state = "aguardando_quantidade"
        self.assistant_message(
            f"Perfeito. Você escolheu **{product['nome']}**. Agora informe a quantidade no seletor abaixo."
        )

    def render_quantity_widget(self):
        if st.session_state.flow_state != "aguardando_quantidade":
            return

        product = st.session_state.current_product
        if not product:
            return

        nome = product["nome"]
        preco = product["preco"]
        unidade = product["unidade"]

        st.markdown("### Quantidade do produto")

        if unidade == "kg":
            quantity = st.number_input(
                label=f"O quilo da {nome} é R$ {preco:.2f}. Quantos quilos você deseja?",
                min_value=1.0,
                value=1.0,
                step=0.1,
                format="%.2f",
                key=f"qty_{nome}",
            )
        else:
            quantity = st.number_input(
                label=f"A unidade de {nome} custa R$ {preco:.2f}. Quantas unidades você deseja?",
                min_value=1,
                value=1,
                step=1,
                format="%d",
                key=f"qty_{nome}",
            )

        subtotal = round(preco * quantity, 2)
        qty_text = f"{quantity:.2f} kg" if unidade == "kg" else f"{int(quantity)} unidade(s)"
        st.write(f"Você escolheu {qty_text} de {nome}.")
        st.write(f"Subtotal: **R$ {subtotal:.2f}**")

        if st.button("Adicionar ao pedido", use_container_width=True, key=f"add_{nome}"):
            item = self.order.add_item(
                st.session_state.cart, product, quantity)
            st.session_state.current_product = None
            st.session_state.flow_state = "aguardando_adicional"
            self.assistant_message(
                f"Adicionei **{item['nome']}** ao seu pedido. Você deseja mais algum modelo de carne ou bebida para acompanhar?"
            )
            st.rerun()

    def _handle_additional_choice(self, lowered: str):
        if any(x in lowered for x in ["sim", "quero", "mais", "adicionar"]):
            if "bebida" in lowered:
                st.session_state.current_group = "bebidas"
                st.session_state.current_category = None
                st.session_state.flow_state = "aguardando_categoria"
                categories = self.catalog.list_drink_categories()
                self.assistant_message(
                    "Perfeito. Estas são as categorias de bebidas:\n\n" +
                    "\n".join([f"{i+1}. {cat}" for i,
                              cat in enumerate(categories)])
                )
                return

            st.session_state.current_group = "carnes"
            st.session_state.current_category = None
            st.session_state.flow_state = "aguardando_categoria"
            categories = self.catalog.list_meat_categories()
            self.assistant_message(
                "Perfeito. Estas são as categorias de carnes:\n\n" +
                "\n".join([f"{i+1}. {cat}" for i,
                          cat in enumerate(categories)])
            )
            return

        if any(x in lowered for x in ["finalizar", "fechar", "confirmar", "concluir"]):
            st.session_state.flow_state = "aguardando_confirmacao_total"
            self.assistant_message(
                "Perfeito. Vou apresentar o total do seu pedido para confirmação.")
            return

        if any(x in lowered for x in ["não", "nao", "só isso", "so isso"]):
            st.session_state.flow_state = "aguardando_confirmacao_total"
            self.assistant_message(
                "Certo. Vou apresentar o total do seu pedido para confirmação.")
            return

        self.assistant_message(
            "Se desejar continuar, me diga se quer **mais carne**, **bebida** ou se deseja **finalizar a compra**."
        )

    def render_order_summary(self):
        if st.session_state.flow_state != "aguardando_confirmacao_total":
            return

        cart = st.session_state.cart
        if not cart:
            st.warning("Seu pedido está vazio.")
            st.session_state.flow_state = "aguardando_intencao"
            return

        st.markdown("### Resumo do pedido")
        for line in self.order.summarize_cart(cart):
            st.write(line)

        total = self.order.get_total(cart)
        st.markdown(f"### Total: R$ {total:.2f}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Adicionar mais itens", use_container_width=True):
                st.session_state.flow_state = "aguardando_adicional"
                self.assistant_message(
                    "Sem problemas. Você deseja adicionar mais carne ou bebida?")
                st.rerun()

        with col2:
            if st.button("Confirmar total", use_container_width=True, type="primary"):
                st.session_state.flow_state = "aguardando_pagamento"
                self.assistant_message(
                    "Perfeito. Escolha a forma de pagamento: **PIX** ou **cartão**.")
                st.rerun()

    def _handle_total_confirmation(self, lowered: str):
        if any(x in lowered for x in ["mais", "adicionar", "voltar"]):
            st.session_state.flow_state = "aguardando_adicional"
            self.assistant_message(
                "Perfeito. Você deseja adicionar mais carne ou bebida?")
            return

        if any(x in lowered for x in ["confirmar", "fechar", "finalizar"]):
            st.session_state.flow_state = "aguardando_pagamento"
            self.assistant_message(
                "Perfeito. Escolha a forma de pagamento: **PIX** ou **cartão**.")
            return

        self.assistant_message(
            "Você pode clicar em **Adicionar mais itens** ou **Confirmar total**.")

    def _handle_payment_choice(self, lowered: str):
        if "pix" in lowered:
            st.session_state.payment_data = {"billing_type": "PIX"}
            self.assistant_message(
                "Perfeito. Vou preparar o pagamento via PIX.")
            return

        if "cart" in lowered:
            st.session_state.payment_data = {"billing_type": "CREDIT_CARD"}
            self.assistant_message(
                "Perfeito. Vou preparar o pagamento via cartão.")
            return

        self.assistant_message(
            "Escolha uma forma de pagamento: **PIX** ou **cartão**.")
