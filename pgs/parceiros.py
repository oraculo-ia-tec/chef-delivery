import streamlit as st


def showParceiros():
    st.title("🤝 Parceiros")
    st.markdown("Gerencie os parceiros cadastrados no Chef Delivery.")

    # --- Filtros ---
    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar parceiro", placeholder="Nome, e-mail ou telefone...")
    with col_filtro:
        filtro_status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"])

    st.markdown("---")

    # --- Lista de parceiros (dados de exemplo) ---
    parceiros_exemplo = [
        {"nome": "Regiane dos Santos", "email": "regiane@gmail.com", "whatsapp": "(31) 99999-0001", "vendas": 42, "status": "Ativo"},
        {"nome": "Alan Teste", "email": "alanteste@gmail.com", "whatsapp": "(31) 99999-0005", "vendas": 18, "status": "Ativo"},
        {"nome": "Grazi Teste", "email": "grazi@gmail.com", "whatsapp": "(31) 99999-0006", "vendas": 25, "status": "Ativo"},
        {"nome": "Dani Teste", "email": "dani@gmail.com", "whatsapp": "(31) 99999-0007", "vendas": 10, "status": "Inativo"},
    ]

    # Aplicar filtro de busca
    if busca:
        busca_lower = busca.lower()
        parceiros_exemplo = [
            p for p in parceiros_exemplo
            if busca_lower in p["nome"].lower()
            or busca_lower in p["email"].lower()
            or busca_lower in p["whatsapp"]
        ]

    # Aplicar filtro de status
    if filtro_status != "Todos":
        parceiros_exemplo = [p for p in parceiros_exemplo if p["status"] == filtro_status]

    # --- Métricas ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Parceiros", len(parceiros_exemplo))
    col2.metric("Ativos", sum(1 for p in parceiros_exemplo if p["status"] == "Ativo"))
    col3.metric("Total de Vendas", sum(p["vendas"] for p in parceiros_exemplo))

    st.markdown("---")

    # --- Tabela de parceiros ---
    if parceiros_exemplo:
        for parceiro in parceiros_exemplo:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3, 3, 2, 1, 1])
                c1.write(f"**{parceiro['nome']}**")
                c2.write(parceiro["email"])
                c3.write(parceiro["whatsapp"])
                c4.write(f"🛒 {parceiro['vendas']}")
                status_color = "🟢" if parceiro["status"] == "Ativo" else "🔴"
                c5.write(f"{status_color} {parceiro['status']}")
            st.markdown("<hr style='margin:0.3rem 0; border-color: rgba(120,255,182,0.1);'>", unsafe_allow_html=True)
    else:
        st.info("Nenhum parceiro encontrado.")

    st.markdown("---")
    st.caption("💡 Em breve: relatório de vendas por parceiro e comissões.")
