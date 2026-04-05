import streamlit as st


def showClientes():
    st.title("👥 Clientes")
    st.markdown("Gerencie os clientes cadastrados no Chef Delivery.")

    tab_listar, tab_criar, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Criar", "✏️ Editar", "🗑️ Deletar"]
    )

    # ── Dados de exemplo ──
    clientes_exemplo = [
        {"nome": "Ramone Teste", "email": "ramone@gmail.com", "whatsapp": "(31) 99999-0001", "pedidos": 5, "status": "Ativo"},
        {"nome": "Adriano Stellantis", "email": "adrianostellantis@gmail.com", "whatsapp": "(31) 99999-0002", "pedidos": 3, "status": "Ativo"},
        {"nome": "Vovô Tec", "email": "vovotec@gmail.com", "whatsapp": "(31) 99999-0003", "pedidos": 1, "status": "Ativo"},
        {"nome": "Usuario Teste", "email": "teste@gmail.com", "whatsapp": "(31) 99999-0004", "pedidos": 0, "status": "Inativo"},
    ]
    clientes_nomes = [c["nome"] for c in clientes_exemplo]

    # ══════════════════════════════════════════════════
    # TAB LISTAR
    # ══════════════════════════════════════════════════
    with tab_listar:
        col_busca, col_filtro = st.columns([3, 1])
        with col_busca:
            busca = st.text_input("🔍 Buscar cliente", placeholder="Nome, e-mail ou telefone...", key="cli_busca")
        with col_filtro:
            filtro_status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"], key="cli_filtro")

        st.markdown("---")

        exibir = list(clientes_exemplo)
        if busca:
            busca_lower = busca.lower()
            exibir = [
                c for c in exibir
                if busca_lower in c["nome"].lower()
                or busca_lower in c["email"].lower()
                or busca_lower in c["whatsapp"]
            ]
        if filtro_status != "Todos":
            status_val = "Ativo" if filtro_status == "Ativos" else "Inativo"
            exibir = [c for c in exibir if c["status"] == status_val]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Clientes", len(exibir))
        col2.metric("Ativos", sum(1 for c in exibir if c["status"] == "Ativo"))
        col3.metric("Pedidos Realizados", sum(c["pedidos"] for c in exibir))

        st.markdown("---")

        if exibir:
            for cliente in exibir:
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

    # ══════════════════════════════════════════════════
    # TAB CRIAR
    # ══════════════════════════════════════════════════
    with tab_criar:
        st.subheader("➕ Cadastrar Novo Cliente")
        with st.form("form_criar_cliente", clear_on_submit=True):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail")
            whatsapp = st.text_input("WhatsApp")
            cpf_cnpj = st.text_input("CPF / CNPJ")
            endereco = st.text_area("Endereço")
            submitted = st.form_submit_button("✅ Cadastrar Cliente", use_container_width=True)
            if submitted:
                if not all([nome, email, whatsapp]):
                    st.error("Preencha os campos obrigatórios: Nome, E-mail e WhatsApp.")
                else:
                    st.success(f"✅ Cliente **{nome}** cadastrado com sucesso!")

    # ══════════════════════════════════════════════════
    # TAB EDITAR
    # ══════════════════════════════════════════════════
    with tab_editar:
        st.subheader("✏️ Editar Cliente")
        cliente_selecionado = st.selectbox("Selecione o cliente", clientes_nomes, key="cli_editar_select")

        dados = next((c for c in clientes_exemplo if c["nome"] == cliente_selecionado), {})
        with st.form("form_editar_cliente"):
            nome_edit = st.text_input("Nome completo", value=dados.get("nome", ""))
            email_edit = st.text_input("E-mail", value=dados.get("email", ""))
            whatsapp_edit = st.text_input("WhatsApp", value=dados.get("whatsapp", ""))
            cpf_cnpj_edit = st.text_input("CPF / CNPJ")
            endereco_edit = st.text_area("Endereço")
            status_edit = st.selectbox("Status", ["Ativo", "Inativo"],
                                       index=0 if dados.get("status") == "Ativo" else 1)
            salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            if salvar:
                st.success(f"✅ Cliente **{nome_edit}** atualizado com sucesso!")

    # ══════════════════════════════════════════════════
    # TAB DELETAR
    # ══════════════════════════════════════════════════
    with tab_deletar:
        st.subheader("🗑️ Remover Cliente")
        st.warning("⚠️ Esta ação é irreversível. O cliente será removido permanentemente.")
        cliente_del = st.selectbox("Selecione o cliente para remover", clientes_nomes, key="cli_del_select")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary", key="cli_del_confirm"):
                st.success(f"✅ Cliente **{cliente_del}** removido com sucesso!")
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="cli_del_cancel"):
                st.info("Exclusão cancelada.")
