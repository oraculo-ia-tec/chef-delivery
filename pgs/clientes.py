import streamlit as st


def showClientes():
    st.title("👥 Clientes")
    st.markdown("Gerencie os clientes cadastrados no Chef Delivery.")

    # --- Filtros ---
    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar cliente", placeholder="Nome, e-mail ou telefone...")
    with col_filtro:
        filtro_status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"])

    st.markdown("---")

    # --- Lista de clientes (dados de exemplo) ---
    clientes_exemplo = [
        {"nome": "Ramone Teste", "email": "ramone@gmail.com", "whatsapp": "(31) 99999-0001", "pedidos": 5, "status": "Ativo"},
        {"nome": "Adriano Stellantis", "email": "adrianostellantis@gmail.com", "whatsapp": "(31) 99999-0002", "pedidos": 3, "status": "Ativo"},
        {"nome": "Vovô Tec", "email": "vovotec@gmail.com", "whatsapp": "(31) 99999-0003", "pedidos": 1, "status": "Ativo"},
        {"nome": "Usuario Teste", "email": "teste@gmail.com", "whatsapp": "(31) 99999-0004", "pedidos": 0, "status": "Inativo"},
    ]

    # Aplicar filtro de busca
    if busca:
        busca_lower = busca.lower()
        clientes_exemplo = [
            c for c in clientes_exemplo
            if busca_lower in c["nome"].lower()
            or busca_lower in c["email"].lower()
            or busca_lower in c["whatsapp"]
        ]

    # Aplicar filtro de status
    if filtro_status != "Todos":
        clientes_exemplo = [c for c in clientes_exemplo if c["status"] == filtro_status]

    # --- Métricas ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Clientes", len(clientes_exemplo))
    col2.metric("Ativos", sum(1 for c in clientes_exemplo if c["status"] == "Ativo"))
    col3.metric("Pedidos Realizados", sum(c["pedidos"] for c in clientes_exemplo))

    st.markdown("---")

    # --- Tabela de clientes ---
    if clientes_exemplo:
        for cliente in clientes_exemplo:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3, 3, 2, 1, 1])
                c1.write(f"**{cliente['nome']}**")
                c2.write(cliente["email"])
                c3.write(cliente["whatsapp"])
                c4.write(f"🛒 {cliente['pedidos']}")
                status_color = "🟢" if cliente["status"] == "Ativo" else "🔴"
                c5.write(f"{status_color} {cliente['status']}")
            st.markdown("<hr style='margin:0.3rem 0; border-color: rgba(120,255,182,0.1);'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente encontrado.")

    st.markdown("---")
    st.caption("💡 Em breve: integração com a base de clientes do ASAAS para sincronização automática.")
