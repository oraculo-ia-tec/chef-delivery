import streamlit as st


def showPagamentos():
    st.title("💳 Pagamentos")
    st.markdown("Acompanhe as cobranças e pagamentos do Chef Delivery.")

    # --- Filtros ---
    col_busca, col_status, col_metodo = st.columns([3, 1, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar pagamento", placeholder="ID, cliente ou descrição...")
    with col_status:
        filtro_status = st.selectbox("Status", ["Todos", "Confirmado", "Pendente", "Vencido", "Cancelado"])
    with col_metodo:
        filtro_metodo = st.selectbox("Método", ["Todos", "PIX", "Cartão", "Boleto"])

    st.markdown("---")

    # --- Dados de exemplo ---
    pagamentos_exemplo = [
        {"id": "pay_001", "cliente": "Ramone Teste", "valor": 149.99, "metodo": "PIX", "status": "Confirmado", "data": "2026-04-04", "descricao": "Kit Churrasco Gold"},
        {"id": "pay_002", "cliente": "Adriano Stellantis", "valor": 89.50, "metodo": "PIX", "status": "Pendente", "data": "2026-04-05", "descricao": "Picanha + Linguiça"},
        {"id": "pay_003", "cliente": "Vovô Tec", "valor": 229.99, "metodo": "Cartão", "status": "Confirmado", "data": "2026-04-03", "descricao": "Kit Churrasco Diamante"},
        {"id": "pay_004", "cliente": "Usuario Teste", "valor": 36.99, "metodo": "PIX", "status": "Vencido", "data": "2026-03-28", "descricao": "1kg Alcatra"},
    ]

    # Aplicar filtros
    if busca:
        busca_lower = busca.lower()
        pagamentos_exemplo = [
            p for p in pagamentos_exemplo
            if busca_lower in p["id"].lower()
            or busca_lower in p["cliente"].lower()
            or busca_lower in p["descricao"].lower()
        ]
    if filtro_status != "Todos":
        pagamentos_exemplo = [p for p in pagamentos_exemplo if p["status"] == filtro_status]
    if filtro_metodo != "Todos":
        pagamentos_exemplo = [p for p in pagamentos_exemplo if p["metodo"] == filtro_metodo]

    # --- Métricas ---
    total_confirmado = sum(p["valor"] for p in pagamentos_exemplo if p["status"] == "Confirmado")
    total_pendente = sum(p["valor"] for p in pagamentos_exemplo if p["status"] == "Pendente")
    total_vencido = sum(p["valor"] for p in pagamentos_exemplo if p["status"] == "Vencido")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cobranças", len(pagamentos_exemplo))
    col2.metric("Confirmados", f"R$ {total_confirmado:,.2f}")
    col3.metric("Pendentes", f"R$ {total_pendente:,.2f}")
    col4.metric("Vencidos", f"R$ {total_vencido:,.2f}")

    st.markdown("---")

    # --- Lista de pagamentos ---
    if pagamentos_exemplo:
        for pag in pagamentos_exemplo:
            status_icons = {
                "Confirmado": "✅",
                "Pendente": "⏳",
                "Vencido": "❌",
                "Cancelado": "🚫",
            }
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

    st.markdown("---")
    st.caption("💡 Em breve: consulta em tempo real via API ASAAS com atualização automática de status.")
