import streamlit as st
import pandas as pd
import base64
from datetime import datetime


def _init_entregadores():
    """Inicializa a lista de entregadores no session_state."""
    if "entregadores" not in st.session_state:
        st.session_state.entregadores = [
            {
                "id": 1,
                "nome": "Carlos Motoboy",
                "email": "carlos.moto@gmail.com",
                "whatsapp": "(31) 99888-0001",
                "modelo_moto": "Honda CG 160 Fan",
                "data_registro": "2026-01-15",
                "horario_registro": "08:30",
                "status": "Ativo",
                "perfil_img": "https://api.dicebear.com/9.x/adventurer/svg?seed=Carlos",
            },
            {
                "id": 2,
                "nome": "Rafael Entregas",
                "email": "rafael.entregas@gmail.com",
                "whatsapp": "(31) 99888-0002",
                "modelo_moto": "Yamaha Factor 150",
                "data_registro": "2026-02-20",
                "horario_registro": "09:15",
                "status": "Ativo",
                "perfil_img": "https://api.dicebear.com/9.x/adventurer/svg?seed=Rafael",
            },
            {
                "id": 3,
                "nome": "Lucas Delivery",
                "email": "lucas.delivery@gmail.com",
                "whatsapp": "(31) 99888-0003",
                "modelo_moto": "Honda Pop 110i",
                "data_registro": "2026-03-10",
                "horario_registro": "10:00",
                "status": "Inativo",
                "perfil_img": "https://api.dicebear.com/9.x/adventurer/svg?seed=Lucas",
            },
        ]


@st.cache_data(show_spinner=False)
def _build_entregador_css() -> str:
    return """
    <style>
    .entregador-card {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        padding: 1rem 1.4rem;
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
        border: 1px solid rgba(120,255,182,0.14);
        margin-bottom: 0.8rem;
        animation: fadeInCard 0.5s ease-out;
    }
    .entregador-card img {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        border: 2px solid rgba(120,255,182,0.3);
        object-fit: cover;
    }
    .entregador-info { flex: 1; }
    .entregador-info .nome { font-weight: 700; font-size: 1.05rem; color: #fff; }
    .entregador-info .detalhe { font-size: 0.88rem; color: #c0d8e8; }
    .status-ativo {
        display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        background: rgba(122,240,176,0.15); border: 1px solid rgba(122,240,176,0.3);
        color: #7af0b0; font-size: 0.82rem; font-weight: 600;
    }
    .status-inativo {
        display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        background: rgba(255,100,100,0.12); border: 1px solid rgba(255,100,100,0.25);
        color: #ff8a8a; font-size: 0.82rem; font-weight: 600;
    }
    @keyframes fadeInCard {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """


def showEntregador():
    st.title("🏍️ Entregadores")
    st.markdown("Cadastro e gerenciamento dos entregadores do Chef Delivery.")

    _init_entregadores()

    # ═══════════════════════════════════════════
    # CSS
    # ═══════════════════════════════════════════
    st.markdown(_build_entregador_css(), unsafe_allow_html=True)

    tab_listar, tab_criar, tab_editar, tab_deletar = st.tabs(
        ["📋 Listar", "➕ Criar", "✏️ Editar", "🗑️ Deletar"]
    )

    todos = st.session_state.entregadores
    entregadores_nomes = [e["nome"] for e in todos]

    # ══════════════════════════════════════════════════
    # TAB LISTAR
    # ══════════════════════════════════════════════════
    with tab_listar:
        col_busca, col_status = st.columns([3, 1])
        with col_busca:
            busca = st.text_input("🔍 Buscar entregador", placeholder="Nome, e-mail ou WhatsApp...", key="ent_busca")
        with col_status:
            filtro_status = st.selectbox("Status", ["Todos", "Ativo", "Inativo"], key="ent_filtro")

        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(todos))
        col2.metric("Ativos", sum(1 for e in todos if e["status"] == "Ativo"))
        col3.metric("Inativos", sum(1 for e in todos if e["status"] == "Inativo"))

        st.markdown("---")

        exibir = list(todos)
        if busca:
            busca_l = busca.lower()
            exibir = [e for e in exibir if busca_l in e["nome"].lower() or busca_l in e["email"].lower() or busca_l in e["whatsapp"]]
        if filtro_status != "Todos":
            exibir = [e for e in exibir if e["status"] == filtro_status]

        if exibir:
            for ent in exibir:
                status_cls = "status-ativo" if ent["status"] == "Ativo" else "status-inativo"
                st.markdown(f"""
                <div class="entregador-card">
                    <img src="{ent['perfil_img']}" alt="{ent['nome']}">
                    <div class="entregador-info">
                        <div class="nome">{ent['nome']}</div>
                        <div class="detalhe">📧 {ent['email']} &nbsp;|&nbsp; 📱 {ent['whatsapp']}</div>
                        <div class="detalhe">🏍️ {ent['modelo_moto']}</div>
                    </div>
                    <span class="{status_cls}">{ent['status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum entregador encontrado.")

        st.markdown("---")
        st.subheader("📊 Registro de Entregadores")

        if todos:
            df = pd.DataFrame(todos)
            df = df.rename(columns={
                "nome": "Nome", "email": "E-mail", "whatsapp": "WhatsApp",
                "modelo_moto": "Modelo da Moto", "data_registro": "Data de Registro",
                "horario_registro": "Horário de Registro", "status": "Status",
            })
            df = df[["Nome", "E-mail", "WhatsApp", "Modelo da Moto", "Data de Registro", "Horário de Registro", "Status"]]
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════
    # TAB CRIAR
    # ══════════════════════════════════════════════════
    with tab_criar:
        st.subheader("➕ Cadastrar Novo Entregador")

        uploaded_img = st.file_uploader(
            "📷 Foto de perfil do entregador",
            type=["png", "jpg", "jpeg", "webp"],
            key="upload_perfil_entregador",
        )
        if uploaded_img is not None:
            col_preview, col_info = st.columns([1, 3])
            with col_preview:
                st.image(uploaded_img, caption="Pré-visualização", width=120)
            with col_info:
                st.caption(f"Arquivo: {uploaded_img.name}")
                st.caption(f"Tamanho: {uploaded_img.size / 1024:.1f} KB")

        with st.form("form_novo_entregador", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                novo_nome = st.text_input("Nome completo")
                novo_email = st.text_input("E-mail")
                novo_whatsapp = st.text_input("WhatsApp")
            with fc2:
                novo_moto = st.text_input("Modelo da moto")
                novo_status = st.selectbox("Status inicial", ["Ativo", "Inativo"])

            submit = st.form_submit_button("✅ Cadastrar Entregador", type="primary", use_container_width=True)

        if submit:
            if not novo_nome:
                st.error("Informe o nome do entregador.", icon="🧑")
                st.stop()
            if not novo_whatsapp:
                st.error("Informe o WhatsApp.", icon="📱")
                st.stop()

            if uploaded_img is not None:
                img_bytes = uploaded_img.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode("ascii")
                ext = uploaded_img.name.rsplit(".", 1)[-1].lower()
                mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
                perfil_img = f"data:{mime};base64,{img_b64}"
            else:
                perfil_img = f"https://api.dicebear.com/9.x/adventurer/svg?seed={novo_nome.split()[0]}"

            agora = datetime.now()
            novo_id = max((e["id"] for e in st.session_state.entregadores), default=0) + 1
            st.session_state.entregadores.append({
                "id": novo_id,
                "nome": novo_nome,
                "email": novo_email or "",
                "whatsapp": novo_whatsapp,
                "modelo_moto": novo_moto or "Não informado",
                "data_registro": agora.strftime("%Y-%m-%d"),
                "horario_registro": agora.strftime("%H:%M"),
                "status": novo_status,
                "perfil_img": perfil_img,
            })
            st.success(f"Entregador **{novo_nome}** cadastrado com sucesso!", icon="✅")
            st.rerun()

    # ══════════════════════════════════════════════════
    # TAB EDITAR
    # ══════════════════════════════════════════════════
    with tab_editar:
        st.subheader("✏️ Editar Entregador")
        if not entregadores_nomes:
            st.info("Nenhum entregador cadastrado.")
        else:
            ent_sel = st.selectbox("Selecione o entregador", entregadores_nomes, key="ent_editar_sel")
            dados = next((e for e in todos if e["nome"] == ent_sel), {})

            with st.form("form_editar_entregador"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    nome_edit = st.text_input("Nome completo", value=dados.get("nome", ""))
                    email_edit = st.text_input("E-mail", value=dados.get("email", ""))
                    whatsapp_edit = st.text_input("WhatsApp", value=dados.get("whatsapp", ""))
                with fc2:
                    moto_edit = st.text_input("Modelo da moto", value=dados.get("modelo_moto", ""))
                    status_edit = st.selectbox("Status", ["Ativo", "Inativo"],
                                               index=0 if dados.get("status") == "Ativo" else 1)

                salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                if salvar:
                    st.success(f"✅ Entregador **{nome_edit}** atualizado com sucesso!")

    # ══════════════════════════════════════════════════
    # TAB DELETAR
    # ══════════════════════════════════════════════════
    with tab_deletar:
        st.subheader("🗑️ Remover Entregador")
        st.warning("⚠️ Esta ação é irreversível. O entregador será removido permanentemente.")

        if not entregadores_nomes:
            st.info("Nenhum entregador cadastrado.")
        else:
            ent_del = st.selectbox("Selecione o entregador para remover", entregadores_nomes, key="ent_del_sel")
            dados_del = next((e for e in todos if e["nome"] == ent_del), {})
            st.info(f"🏍️ {dados_del.get('modelo_moto', '')} | 📱 {dados_del.get('whatsapp', '')}")

            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary", key="ent_del_confirm"):
                    st.success(f"✅ Entregador **{ent_del}** removido com sucesso!")
            with col_cancel:
                if st.button("❌ Cancelar", use_container_width=True, key="ent_del_cancel"):
                    st.info("Exclusão cancelada.")
