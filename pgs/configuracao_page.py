import streamlit as st


def showConfiguracao():
    st.title("⚙️ Configuração")
    st.markdown("Gerencie as configurações do sistema Chef Delivery.")

    # --- Seção: Informações da Loja ---
    st.subheader("🏪 Informações da Loja")
    with st.form("config_loja"):
        nome_loja = st.text_input("Nome da Loja", value="Chef Delivery")
        telefone_loja = st.text_input("Telefone/WhatsApp", value="(31) 98341-7976")
        endereco_loja = st.text_input("Endereço", value="")
        raio_entrega = st.number_input("Raio de entrega (km)", min_value=1, max_value=50, value=5)
        taxa_entrega = st.number_input("Taxa de entrega (R$)", min_value=0.0, step=0.50, value=6.0, format="%.2f")
        salvar_loja = st.form_submit_button("Salvar Informações")
        if salvar_loja:
            st.success("Informações da loja salvas com sucesso!", icon="✅")

    st.markdown("---")

    # --- Seção: Configuração de Pagamento ---
    st.subheader("💳 Configuração de Pagamento (ASAAS)")

    asaas_key = st.secrets.get("api_keys", {}).get("ASAAS_API_KEY", "")
    if asaas_key:
        st.success("API Key ASAAS configurada", icon="✅")
        ambiente = st.radio("Ambiente", ["Sandbox (testes)", "Produção"], index=0, horizontal=True)
        if ambiente == "Produção":
            st.warning("⚠️ O ambiente de produção processa pagamentos reais. Verifique antes de ativar.")
    else:
        st.error("API Key ASAAS não configurada. Adicione em .streamlit/secrets.toml", icon="❌")

    st.markdown("---")

    # --- Seção: Métodos de Pagamento ---
    st.subheader("📋 Métodos de Pagamento Ativos")
    col1, col2, col3 = st.columns(3)
    with col1:
        pix_ativo = st.toggle("PIX", value=True)
    with col2:
        cartao_ativo = st.toggle("Cartão de Crédito", value=False)
    with col3:
        boleto_ativo = st.toggle("Boleto", value=False)

    if pix_ativo:
        st.info("PIX: Cobrança gerada automaticamente com QR Code via ASAAS.")
    if cartao_ativo:
        st.info("Cartão: Redirecionamento para checkout seguro do ASAAS.")
    if boleto_ativo:
        st.info("Boleto: Gerado automaticamente com vencimento configurável.")

    st.markdown("---")

    # --- Seção: Webhooks ---
    st.subheader("🔗 Webhooks e Integrações")

    webhook_url = st.secrets.get("api_keys", {}).get("WEBHOOK_URL", "")
    webhook_cadastro = st.secrets.get("api_keys", {}).get("WEBHOOK_CADASTRO", "")

    with st.expander("Ver configuração de webhooks"):
        st.text_input("Webhook de Pedidos", value=webhook_url, disabled=True)
        st.text_input("Webhook de Cadastro", value=webhook_cadastro, disabled=True)
        st.caption("Para alterar os webhooks, edite o arquivo .streamlit/secrets.toml")

    st.markdown("---")

    # --- Seção: Usuários ---
    st.subheader("👤 Usuários do Sistema")

    users_list = st.secrets.get("credentials", {}).get("users", [])
    if users_list:
        for user in users_list:
            role_icon = {"admin": "🔑", "parceiro": "🤝", "cliente": "👤"}.get(user.get("role", ""), "❔")
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"**{user['name']}** ({user['username']})")
                c2.write(user.get("email", ""))
                c3.write(f"{role_icon} {user.get('role', 'N/A')}")
            st.markdown("<hr style='margin:0.2rem 0; border-color: rgba(120,255,182,0.08);'>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum usuário configurado.")

    st.markdown("---")
    st.caption("💡 As configurações sensíveis (API keys, webhooks) são gerenciadas via secrets.toml por segurança.")
