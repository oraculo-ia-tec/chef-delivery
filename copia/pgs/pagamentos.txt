import streamlit as st


def showPagamentos():
    st.title("💳 Pagamentos")
    st.markdown("Acompanhe as cobranças e pagamentos do Chef Delivery.")

    tab_listar, tab_consultar, tab_estornar = st.tabs(
        ["📋 Listar", "🔍 Consultar", "↩️ Estornar / Cancelar"]
    )

    # ── Dados de exemplo ──
    pagamentos_exemplo = [
        {"id": "pay_001", "cliente": "Ramone Teste", "valor": 149.99, "metodo": "PIX", "status": "Confirmado", "data": "2026-04-04", "descricao": "Kit Churrasco Gold"},
        {"id": "pay_002", "cliente": "Adriano Stellantis", "valor": 89.50, "metodo": "PIX", "status": "Pendente", "data": "2026-04-05", "descricao": "Picanha + Linguiça"},
        {"id": "pay_003", "cliente": "Vovô Tec", "valor": 229.99, "metodo": "Cartão", "status": "Confirmado", "data": "2026-04-03", "descricao": "Kit Churrasco Diamante"},
        {"id": "pay_004", "cliente": "Usuario Teste", "valor": 36.99, "metodo": "PIX", "status": "Vencido", "data": "2026-03-28", "descricao": "1kg Alcatra"},
    ]

    # ══════════════════════════════════════════════════
    # TAB LISTAR
    # ══════════════════════════════════════════════════
    with tab_listar:
        col_busca, col_status, col_metodo = st.columns([3, 1, 1])
        with col_busca:
            busca = st.text_input("🔍 Buscar pagamento", placeholder="ID, cliente ou descrição...", key="pag_busca")
        with col_status:
            filtro_status = st.selectbox("Status", ["Todos", "Confirmado", "Pendente", "Vencido", "Cancelado"], key="pag_status")
        with col_metodo:
            filtro_metodo = st.selectbox("Método", ["Todos", "PIX", "Cartão", "Boleto"], key="pag_metodo")

        st.markdown("---")

        exibir = list(pagamentos_exemplo)
        if busca:
            busca_lower = busca.lower()
            exibir = [
                p for p in exibir
                if busca_lower in p["id"].lower()
                or busca_lower in p["cliente"].lower()
                or busca_lower in p["descricao"].lower()
            ]
        if filtro_status != "Todos":
            exibir = [p for p in exibir if p["status"] == filtro_status]
        if filtro_metodo != "Todos":
            exibir = [p for p in exibir if p["metodo"] == filtro_metodo]

        total_confirmado = sum(p["valor"] for p in exibir if p["status"] == "Confirmado")
        total_pendente = sum(p["valor"] for p in exibir if p["status"] == "Pendente")
        total_vencido = sum(p["valor"] for p in exibir if p["status"] == "Vencido")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cobranças", len(exibir))
        col2.metric("Confirmados", f"R$ {total_confirmado:,.2f}")
        col3.metric("Pendentes", f"R$ {total_pendente:,.2f}")
        col4.metric("Vencidos", f"R$ {total_vencido:,.2f}")

        st.markdown("---")

        if exibir:
            for pag in exibir:
                status_icons = {"Confirmado": "✅", "Pendente": "⏳", "Vencido": "❌", "Cancelado": "🚫"}
                icone = status_icons.get(pag["status"], "❔")
                with st.container():
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 3, 2, 1, 2, 1])
                    c1.write(f"`{pag['id']}`")
                    c2.write(f"**{pag['cliente']}**")
                    c3.write(pag["descricao"])
                    c4.write(pag["metodo"])
                    c5.write(f"R$ {pag['valor']:,.2f}")
                    c6.write(f"{icone} {pag['status']}")
                st.markdown("<hr style='margin:0.3rem 0; border-color: rgba(120,255,182,0.1);'>", unsafe_allow_html=True)
        else:
            st.info("Nenhum pagamento encontrado.")

    # ══════════════════════════════════════════════════
    # TAB CONSULTAR
    # ══════════════════════════════════════════════════
    with tab_consultar:
        st.subheader("🔍 Consultar Pagamento")
        payment_id = st.text_input("ID do pagamento (ex: pay_001)", key="pag_consulta_id")
        if st.button("🔎 Consultar", use_container_width=True, key="pag_consulta_btn"):
            if not payment_id:
                st.error("Informe o ID do pagamento.")
            else:
                encontrado = next((p for p in pagamentos_exemplo if p["id"] == payment_id), None)
                if encontrado:
                    st.success(f"Pagamento encontrado: **{encontrado['id']}**")
                    col1, col2 = st.columns(2)
                    col1.metric("Cliente", encontrado["cliente"])
                    col2.metric("Valor", f"R$ {encontrado['valor']:,.2f}")
                    col1.metric("Método", encontrado["metodo"])
                    col2.metric("Status", encontrado["status"])
                    st.info(f"📅 Data: {encontrado['data']} | 📝 {encontrado['descricao']}")
                else:
                    st.warning(f"Nenhum pagamento com ID **{payment_id}** encontrado.")

    # ══════════════════════════════════════════════════
    # TAB ESTORNAR / CANCELAR
    # ══════════════════════════════════════════════════
    with tab_estornar:
        st.subheader("↩️ Estornar ou Cancelar Pagamento")
        st.warning("⚠️ Estornos e cancelamentos são irreversíveis. Confirme antes de prosseguir.")

        pag_ids = [p["id"] for p in pagamentos_exemplo]
        pag_sel = st.selectbox("Selecione o pagamento", pag_ids, key="pag_estorno_sel")
        pag_info = next((p for p in pagamentos_exemplo if p["id"] == pag_sel), None)

        if pag_info:
            st.info(f"**{pag_info['cliente']}** — R$ {pag_info['valor']:,.2f} — {pag_info['status']}")

        acao = st.radio("Ação", ["Cancelar cobrança", "Estornar pagamento"], key="pag_estorno_acao", horizontal=True)
        motivo = st.text_area("Motivo (opcional)", key="pag_estorno_motivo")

        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("✅ Confirmar Ação", use_container_width=True, type="primary", key="pag_estorno_confirm"):
                st.success(f"✅ {acao} realizado para **{pag_sel}**!")
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="pag_estorno_cancel"):
                st.info("Ação cancelada.")
