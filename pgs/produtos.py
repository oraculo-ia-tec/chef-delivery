import streamlit as st
import asyncio
import uuid
import base64
from datetime import date, timedelta
from decimal import Decimal

from api_asaas import (
    AsaasConfig,
    AsaasClient,
    CustomerCreateInput,
    PaymentCreateInput,
)
from config import ASAAS_API_KEY, ASAAS_ENVIRONMENT


# ─────────────────────────────────────────────
# Catálogo de produtos do Chef Delivery
# ─────────────────────────────────────────────

CATEGORIAS = {
    "🥩 Boi": {
        "unidade": "kg",
        "itens": {
            "Alcatra (peça)": 32.99,
            "Alcatra (kg)": 36.99,
            "Contra filé (peça)": 34.99,
            "Contra filé (kg)": 37.99,
            "Chã de dentro (peça)": 28.99,
            "Chã de dentro (kg)": 33.99,
            "Chã de fora (peça)": 29.99,
            "Chã de fora (kg)": 33.99,
            "Patinho (peça)": 27.99,
            "Patinho (kg)": 33.99,
            "Pá completa (peça)": 24.99,
            "Miolo de acém (peça)": 24.99,
            "Miolo de acém (kg)": 29.99,
            "Maçã de peito (peça)": 24.99,
            "Maçã de peito (kg)": 29.99,
            "Picanha Premiata": 79.99,
            "Picanha Dia a Dia": 49.99,
            "Filé Mignon c/ cordão": 49.99,
            "Maminha": 37.99,
            "Miolo de alcatra": 39.99,
            "Lagarto": 33.99,
            "Lagarto recheado": 34.99,
            "Lagartinho": 33.99,
            "Garrão": 29.99,
            "Acém": 24.99,
            "Pá/Paleta": 29.99,
            "Capa de filé": 29.99,
            "Músculo dianteiro": 29.99,
            "Músculo traseiro": 29.99,
            "Fraldinha": 34.99,
            "Fraldão": 39.99,
            "Cupim": 35.99,
            "Costelão inteiro": 24.99,
            "Costela de boi": 19.99,
            "Costela gaúcha": 19.99,
            "Costelão especial": 21.99,
            "Costela recheada": 34.99,
            "Costela desossada": 49.99,
            "Carne de sol 2ª": 34.99,
            "Chãzinha": 29.99,
            "Rabada": 35.99,
            "Dobradinha": 15.99,
            "Dobradinha colméia": 24.99,
            "Fígado (bife)": 14.99,
            "Língua de boi": 16.99,
            "Coração de boi": 9.99,
            "Mocotó": 10.99,
            "Moída promoção": 19.99,
            "Acém promocional": 19.99,
        },
    },
    "🐷 Porco": {
        "unidade": "kg",
        "itens": {
            "Bisteca": 16.99,
            "Tomahawk suíno": 21.99,
            "Pazinha PC": 15.99,
            "Pazinha": 16.99,
            "Pazinha pele e osso": 14.99,
            "Pazinha pele s/ osso": 15.99,
            "Pazinha defumada": 29.99,
            "Pernil PC": 16.99,
            "Pernil": 18.99,
            "Pernil recheado": 21.99,
            "Lombo PC": 18.99,
            "Lombo": 19.99,
            "Lombo com pele": 18.99,
            "Lombo defumado": 29.99,
            "Lombo recheado": 23.99,
            "Copa lombo": 21.99,
            "Lombinho": 21.99,
            "Picanha suína": 26.99,
            "Costelinha c/ lombo": 20.99,
            "Costelinha aparada": 24.99,
            "Costelinha defumada": 34.99,
            "Rabinho": 21.99,
            "Bacon": 29.99,
            "Toucinho comum": 9.99,
            "Toucinho especial": 21.99,
        },
    },
    "🍗 Frango": {
        "unidade": "kg",
        "itens": {
            "Frango resfriado": 10.99,
            "Coxa e sobrecoxa": 9.99,
            "Peito de frango": 14.99,
            "Asa de frango": 14.99,
            "Dorso": 4.49,
            "Pezinho de frango": 7.99,
        },
    },
    "🌭 Linguiça / Embutidos": {
        "unidade": "kg",
        "itens": {
            "Linguiça toscana FM": 14.99,
            "Linguiça defumada": 19.99,
            "Linguiça de frango gomo": 21.99,
            "Linguiça de frango fina": 24.99,
            "Linguiça pernil fina": 24.99,
            "Linguiça caseira": 19.99,
            "Linguiça caipira": 24.99,
            "Linguiça de costela": 24.99,
            "Calabresa": 22.99,
            "Salsicha Pif Paf": 10.99,
            "Salsicha Perdigão": 11.99,
            "Salsichão": 13.99,
            "Salaminho": 16.99,
        },
    },
    "🐟 Peixe": {
        "unidade": "kg",
        "itens": {
            "Cavalinha": 10.99,
            "Sardinha": 14.99,
            "Filé de Merluza": 39.99,
            "Cascudo": 17.99,
            "Filé de Tilápia": 49.99,
        },
    },
    "🔥 Kits Churrasco": {
        "unidade": "un",
        "itens": {
            "Kit Diamante": 229.99,
            "Kit Gold+": 169.99,
            "Kit Gold": 149.99,
            "Kit Prata+": 149.99,
            "Kit Prata": 129.99,
            "Kit Bronze": 99.99,
            "Kit Economia": 109.99,
        },
    },
    "🥤 Bebidas": {
        "unidade": "un",
        "itens": {
            "Fanta PET 200ml": 2.99,
            "Coca-Cola PET 200ml": 2.99,
            "Fanta 2L PET": 9.99,
            "Retornável 2L": 7.50,
            "Coca Zero 600ml": 6.99,
            "Suco Del Vale 290ml": 4.99,
            "Lata Coca-Cola 350ml": 4.99,
            "Lata Fanta 350ml": 4.99,
            "Powerade": 4.99,
            "Água s/ gás 500ml": 3.00,
            "Água c/ gás 500ml": 3.00,
        },
    },
    "🧂 Acompanhamentos": {
        "unidade": "un",
        "itens": {
            "Pão de Alho Shamara": 9.99,
            "Pão de Alho Zé do Espeto": 21.99,
            "Pão de Alho Dona Beth": 21.99,
            "Carvão 3kg": 14.99,
            "Carvão 10kg": 39.99,
            "Sal grosso": 2.99,
            "Tempero pote 300g": 4.99,
            "Molho 150ml": 3.99,
            "Torresmo pré-frito (kg)": 44.90,
            "Torresmo D'Abadia": 10.99,
            "Torresmo Santa Fé": 10.99,
            "Banha 900ml": 16.99,
        },
    },
}

KITS_DESCRICAO = {
    "Kit Diamante": "1 picanha Grill (~1,3-1,5kg) + 1kg lombo + 1kg asa + 1kg linguiça gourmet + carvão 3kg + pão de alho Zé do Espeto — Serve ~10 pessoas",
    "Kit Gold+": "1 picanha Grill (~1kg) + 1kg lombo/copa + 1kg asa/coxinha + 1kg linguiça gourmet + carvão 3kg + pão de alho — Serve ~10 pessoas",
    "Kit Gold": "1 picanha Grill (~1kg) + 1kg lombo/copa + 1kg asa/coxinha + 1kg linguiça gourmet + carvão 3kg — Serve ~10 pessoas",
    "Kit Prata+": "1kg Ancho/Chorizo + 1kg pernil/copa + 1kg asa/coxinha + 1kg linguiça gourmet + carvão 3kg + pão de alho — Serve ~10 pessoas",
    "Kit Prata": "1kg Ancho/Chorizo + 1kg pernil/copa + 1kg asa/coxinha + 1kg linguiça gourmet + carvão 3kg — Serve ~10 pessoas",
    "Kit Bronze": "1kg Chã de Dentro + 1kg Pernil + 1kg Asa + 1kg Linguiça Toscana + carvão 3kg — Serve ~10 pessoas",
    "Kit Economia": "1kg frango a passarinho + 1kg carne p/ cozinhar + 1kg moída + 1kg linguiça + 1kg bife pernil + 1kg bisteca — Serve ~10 pessoas",
}


def _init_carrinho():
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []


async def _gerar_cobranca_pix(nome_cliente: str, total: float, descricao: str) -> dict:
    """Cria cliente + cobrança PIX no ASAAS e retorna payment + QR Code."""
    config = AsaasConfig(api_key=ASAAS_API_KEY, environment=ASAAS_ENVIRONMENT)
    client = AsaasClient(config)

    async with client:
        # Cria ou reutiliza cliente
        customer_payload = CustomerCreateInput(name=nome_cliente)
        customer = await client.create_or_get_customer(customer_payload)
        customer_id = customer["id"]

        # Cria cobrança PIX
        due_date = (date.today() + timedelta(days=1)).isoformat()
        order_id = f"PROD-{uuid.uuid4().hex[:8].upper()}"

        payment_data = await client.create_pix_payment(
            PaymentCreateInput(
                customer=customer_id,
                billing_type="PIX",
                value=total,
                due_date=due_date,
                description=descricao,
                external_reference=order_id,
            )
        )

        # Busca QR Code
        qr = await client.get_pix_qr_code(payment_data["id"])

        return {
            "payment_id": payment_data.get("id"),
            "status": payment_data.get("status"),
            "value": payment_data.get("value"),
            "invoice_url": payment_data.get("invoiceUrl"),
            "pix_payload": qr.payload,
            "pix_qr_code_base64": qr.encoded_image,
            "pix_expiration_date": qr.expiration_date,
            "order_id": order_id,
        }


def showProdutos():
    st.title("📦 Produtos")
    st.markdown("Catálogo de produtos do Chef Delivery — selecione, monte o pedido e gere o pagamento PIX.")

    _init_carrinho()

    # ──────────── ABAS ────────────
    tab_catalogo, tab_carrinho, tab_criar, tab_editar, tab_deletar = st.tabs(
        ["🛒 Catálogo", "📋 Carrinho & Pagamento", "➕ Criar Produto", "✏️ Editar Produto", "🗑️ Deletar Produto"]
    )

    # ═══════════════════════════════════════════
    # TAB 1 — CATÁLOGO
    # ═══════════════════════════════════════════
    with tab_catalogo:
        # Seletor de categoria
        categoria_nome = st.segmented_control(
            "Categoria",
            options=list(CATEGORIAS.keys()),
            default="🥩 Boi",
        )

        if categoria_nome:
            cat = CATEGORIAS[categoria_nome]
            unidade = cat["unidade"]
            itens = cat["itens"]
            label_un = "kg" if unidade == "kg" else "un"

            st.markdown(f"**{len(itens)} produtos** — preços por **{label_un}**")
            st.markdown("---")

            # Exibe produtos em grid 2 colunas
            itens_list = list(itens.items())
            for i in range(0, len(itens_list), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(itens_list):
                        break
                    nome_produto, preco = itens_list[idx]

                    with col:
                        with st.container(border=True):
                            st.markdown(f"### {nome_produto}")
                            st.markdown(f"**R$ {preco:,.2f}** / {label_un}")

                            # Descrição extra para kits
                            if nome_produto in KITS_DESCRICAO:
                                st.caption(KITS_DESCRICAO[nome_produto])

                            # Quantidade
                            if unidade == "kg":
                                qtd = st.number_input(
                                    f"Quantidade ({label_un})",
                                    min_value=1.0,
                                    max_value=100.0,
                                    value=1.0,
                                    step=0.5,
                                    format="%.1f",
                                    key=f"qtd_{categoria_nome}_{nome_produto}",
                                )
                            else:
                                qtd = st.number_input(
                                    f"Quantidade ({label_un})",
                                    min_value=1,
                                    max_value=100,
                                    value=1,
                                    step=1,
                                    key=f"qtd_{categoria_nome}_{nome_produto}",
                                )

                            subtotal = round(float(preco) * float(qtd), 2)
                            st.markdown(f"**Subtotal: R$ {subtotal:,.2f}**")

                            if st.button("➕ Adicionar", key=f"add_{categoria_nome}_{nome_produto}"):
                                st.session_state.carrinho.append({
                                    "produto": nome_produto,
                                    "preco_unit": preco,
                                    "qtd": float(qtd),
                                    "unidade": label_un,
                                    "subtotal": subtotal,
                                })
                                st.success(f"{nome_produto} — {qtd} {label_un} adicionado!", icon="✅")
                                st.rerun()

    # ═══════════════════════════════════════════
    # TAB 2 — CARRINHO & PAGAMENTO
    # ═══════════════════════════════════════════
    with tab_carrinho:
        carrinho = st.session_state.carrinho

        if not carrinho:
            st.info("Seu carrinho está vazio. Adicione produtos no catálogo.")
            return

        st.subheader("Itens do Pedido")

        total_geral = 0.0
        itens_para_remover = []

        for i, item in enumerate(carrinho):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 2, 2, 1])
            c1.write(f"**{item['produto']}**")
            c2.write(f"{item['qtd']} {item['unidade']}")
            c3.write(f"R$ {item['preco_unit']:,.2f}/{item['unidade']}")
            c4.write(f"**R$ {item['subtotal']:,.2f}**")
            if c5.button("🗑️", key=f"rm_{i}"):
                itens_para_remover.append(i)
            total_geral += item["subtotal"]

        # Remover itens marcados
        if itens_para_remover:
            for idx in sorted(itens_para_remover, reverse=True):
                st.session_state.carrinho.pop(idx)
            st.rerun()

        st.markdown("---")

        # Taxa de entrega
        taxa_entrega = 6.00
        st.markdown(f"**Subtotal:** R$ {total_geral:,.2f}")
        st.markdown(f"**Taxa de entrega:** R$ {taxa_entrega:,.2f}")
        total_final = round(total_geral + taxa_entrega, 2)
        st.markdown(f"### 💰 Total: R$ {total_final:,.2f}")

        st.markdown("---")

        # Limpar carrinho
        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

        st.markdown("---")

        # ── Dados do cliente + gerar pagamento ──
        st.subheader("Dados para Pagamento")

        nome_cliente = st.text_input("Nome completo", key="prod_nome_cliente")
        whatsapp = st.text_input("WhatsApp", key="prod_whatsapp")

        gerar = st.button("🔑 Gerar Cobrança PIX", type="primary", disabled=not ASAAS_API_KEY)

        if gerar:
            if not nome_cliente:
                st.error("Informe o nome do cliente.", icon="🧑")
                st.stop()
            if not whatsapp:
                st.error("Informe o WhatsApp.", icon="📱")
                st.stop()

            # Monta descrição
            descricao_itens = " | ".join(
                f"{item['produto']} {item['qtd']}{item['unidade']}" for item in carrinho
            )
            descricao = f"Chef Delivery: {descricao_itens}"
            if len(descricao) > 500:
                descricao = descricao[:497] + "..."

            with st.spinner("Gerando cobrança PIX via ASAAS..."):
                try:
                    result = asyncio.run(
                        _gerar_cobranca_pix(nome_cliente, total_final, descricao)
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar cobrança: {e}", icon="❌")
                    st.stop()

            st.success("Cobrança PIX gerada com sucesso!", icon="✅")

            # QR Code
            if result.get("pix_qr_code_base64"):
                qr_bytes = base64.b64decode(result["pix_qr_code_base64"])
                col_qr, col_info = st.columns([1, 1])
                with col_qr:
                    st.image(qr_bytes, caption="Escaneie o QR Code para pagar", width=300)
                with col_info:
                    st.metric("Valor", f"R$ {total_final:,.2f}")
                    if result.get("pix_expiration_date"):
                        st.info(f"⏰ Validade: {result['pix_expiration_date']}")
                    if result.get("invoice_url"):
                        st.markdown(f"[🔗 Link de pagamento]({result['invoice_url']})")
                    st.caption(f"ID: {result.get('payment_id', '')}")
                    st.caption(f"Pedido: {result.get('order_id', '')}")

            # Copia e cola
            if result.get("pix_payload"):
                st.text_area(
                    "PIX Copia e Cola",
                    value=result["pix_payload"],
                    height=100,
                    help="Copie este código e cole no app do seu banco",
                )

    # ═══════════════════════════════════════════
    # TAB 3 — CRIAR PRODUTO
    # ═══════════════════════════════════════════
    with tab_criar:
        st.subheader("➕ Cadastrar Novo Produto")
        with st.form("form_criar_produto", clear_on_submit=True):
            cat_criar = st.selectbox("Categoria", list(CATEGORIAS.keys()), key="prod_criar_cat")
            nome_prod = st.text_input("Nome do produto")
            preco_prod = st.number_input("Preço (R$)", min_value=0.01, step=0.50, format="%.2f")
            unidade_prod = st.selectbox("Unidade", ["kg", "un"])
            descricao_prod = st.text_area("Descrição (opcional)")
            submitted = st.form_submit_button("✅ Cadastrar Produto", use_container_width=True)
            if submitted:
                if not nome_prod:
                    st.error("Informe o nome do produto.")
                else:
                    st.success(f"✅ Produto **{nome_prod}** cadastrado em {cat_criar} por R$ {preco_prod:,.2f}/{unidade_prod}!")

    # ═══════════════════════════════════════════
    # TAB 4 — EDITAR PRODUTO
    # ═══════════════════════════════════════════
    with tab_editar:
        st.subheader("✏️ Editar Produto")
        cat_editar = st.selectbox("Categoria", list(CATEGORIAS.keys()), key="prod_editar_cat")
        itens_cat = list(CATEGORIAS[cat_editar]["itens"].keys())
        produto_sel = st.selectbox("Produto", itens_cat, key="prod_editar_sel")

        preco_atual = CATEGORIAS[cat_editar]["itens"].get(produto_sel, 0)
        unidade_atual = CATEGORIAS[cat_editar]["unidade"]

        with st.form("form_editar_produto"):
            nome_edit = st.text_input("Nome do produto", value=produto_sel)
            preco_edit = st.number_input("Preço (R$)", min_value=0.01, step=0.50, value=float(preco_atual), format="%.2f")
            unidade_edit = st.selectbox("Unidade", ["kg", "un"], index=0 if unidade_atual == "kg" else 1)
            descricao_edit = st.text_area("Descrição (opcional)")
            salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            if salvar:
                st.success(f"✅ Produto **{nome_edit}** atualizado para R$ {preco_edit:,.2f}/{unidade_edit}!")

    # ═══════════════════════════════════════════
    # TAB 5 — DELETAR PRODUTO
    # ═══════════════════════════════════════════
    with tab_deletar:
        st.subheader("🗑️ Remover Produto")
        st.warning("⚠️ Esta ação é irreversível. O produto será removido do catálogo.")
        cat_del = st.selectbox("Categoria", list(CATEGORIAS.keys()), key="prod_del_cat")
        itens_del = list(CATEGORIAS[cat_del]["itens"].keys())
        produto_del = st.selectbox("Produto", itens_del, key="prod_del_sel")

        preco_del = CATEGORIAS[cat_del]["itens"].get(produto_del, 0)
        st.info(f"**{produto_del}** — R$ {preco_del:,.2f}")

        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary", key="prod_del_confirm"):
                st.success(f"✅ Produto **{produto_del}** removido com sucesso!")
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="prod_del_cancel"):
                st.info("Exclusão cancelada.")
