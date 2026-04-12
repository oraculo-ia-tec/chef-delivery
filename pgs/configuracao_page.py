import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def showConfiguracao():
    st.title("⚙️ Configuração")
    st.markdown("Gerencie as configurações do sistema Chef Delivery.")

    tab_loja, tab_pagamento, tab_webhooks, tab_usuarios = st.tabs(
        ["🏪 Loja", "💳 Pagamento", "🔗 Webhooks", "👤 Usuários"]
    )

    # ══════════════════════════════════════════════════
    # TAB LOJA
    # ══════════════════════════════════════════════════
    with tab_loja:
        st.subheader("🏪 Informações da Loja")
        with st.form("config_loja"):
            nome_loja = st.text_input("Nome da Loja", value="Chef Delivery")
            telefone_loja = st.text_input("Telefone/WhatsApp", value="(31) 98341-7976")
            endereco_loja = st.text_input("Endereço", value="")
            raio_entrega = st.number_input("Raio de entrega (km)", min_value=1, max_value=50, value=5)
            taxa_entrega = st.number_input("Taxa de entrega (R$)", min_value=0.0, step=0.50, value=6.0, format="%.2f")
            salvar_loja = st.form_submit_button("💾 Salvar Informações", use_container_width=True)
            if salvar_loja:
                st.success("Informações da loja salvas com sucesso!", icon="✅")

    # ══════════════════════════════════════════════════
    # TAB PAGAMENTO
    # ══════════════════════════════════════════════════
    with tab_pagamento:
        st.subheader("💳 Configuração de Pagamento (ASAAS)")

        asaas_key = os.getenv("ASAAS_API_KEY", "")
        if asaas_key:
            st.success("API Key ASAAS configurada", icon="✅")
            ambiente = st.radio("Ambiente", ["Sandbox (testes)", "Produção"], index=0, horizontal=True)
            if ambiente == "Produção":
                st.warning("⚠️ O ambiente de produção processa pagamentos reais. Verifique antes de ativar.")
        else:
            st.error("API Key ASAAS não configurada. Adicione no arquivo .env", icon="❌")

        st.markdown("---")

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

    # ══════════════════════════════════════════════════
    # TAB WEBHOOKS
    # ══════════════════════════════════════════════════
    with tab_webhooks:
        st.subheader("🔗 Webhooks e Integrações")

        webhook_url = os.getenv("WEBHOOK_URL", "")
        webhook_cadastro = os.getenv("WEBHOOK_CADASTRO", "")

        st.text_input("Webhook de Pedidos", value=webhook_url, disabled=True)
        st.text_input("Webhook de Cadastro", value=webhook_cadastro, disabled=True)
        st.caption("Para alterar os webhooks, edite o arquivo .env")

    # ══════════════════════════════════════════════════
    # TAB USUÁRIOS
    # ══════════════════════════════════════════════════
    with tab_usuarios:
        st.subheader("👤 Usuários do Sistema")

        from database import create_session as _db_session
        from database.repositories import usuario_repo

        async def _load_users():
            session = await _db_session()
            try:
                return await usuario_repo.list_usuarios(session)
            finally:
                await session.close()

        db_users = asyncio.run(_load_users())

        tab_u_listar, tab_u_cadastrar, tab_u_editar, tab_u_deletar = st.tabs(
            ["📋 Listar", "➕ Cadastrar", "✏️ Editar", "🗑️ Deletar"]
        )

        with tab_u_listar:
            if db_users:
                for user in db_users:
                    role_icon = {"admin": "🔑", "parceiro": "🤝", "cliente": "👤", "entregador": "🏍️", "funcionario": "👷"}.get(user.role, "❔")
                    verificado = "✅" if user.email_verificado else "⏳"
                    with st.container():
                        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                        c1.write(f"**{user.nome}**")
                        c2.write(user.email)
                        c3.write(f"{role_icon} {user.role}")
                        c4.write(verificado)
                    st.markdown("<hr style='margin:0.2rem 0; border-color: rgba(120,255,182,0.08);'>", unsafe_allow_html=True)
            else:
                st.warning("Nenhum usuário cadastrado.")

        with tab_u_cadastrar:
            st.subheader("➕ Cadastrar Novo Usuário")
            from database.services.auth_service import hash_password as _hash_pw
            
            with st.form("form_cadastrar_usuario"):
                nome_novo = st.text_input("Nome completo", placeholder="Ex: João da Silva")
                email_novo = st.text_input("E-mail", placeholder="Ex: joao@email.com")
                whatsapp_novo = st.text_input("WhatsApp", placeholder="Ex: 31999990000")
                senha_novo = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
                role_novo = st.selectbox("Cargo", ["cliente", "parceiro", "entregador", "funcionario", "admin"],
                                         help="Selecione o tipo de usuário")
                verificado_novo = st.toggle("E-mail já verificado", value=False)
                cadastrar_btn = st.form_submit_button("👤 Cadastrar Usuário", use_container_width=True, type="primary")
                
                if cadastrar_btn:
                    if not nome_novo or not email_novo or not whatsapp_novo or not senha_novo:
                        st.error("Preencha todos os campos obrigatórios!")
                    elif len(senha_novo) < 6:
                        st.error("A senha deve ter no mínimo 6 caracteres!")
                    else:
                        async def _create_user():
                            session = await _db_session()
                            try:
                                # Verifica se email já existe
                                existing = await usuario_repo.get_usuario_by_email(session, email_novo)
                                if existing:
                                    return {"success": False, "error": f"E-mail {email_novo} já está cadastrado!"}
                                
                                senha_hash = _hash_pw(senha_novo)
                                novo_user = await usuario_repo.create_usuario(
                                    session,
                                    nome=nome_novo,
                                    email=email_novo,
                                    whatsapp=whatsapp_novo,
                                    senha_hash=senha_hash,
                                    role=role_novo,
                                )
                                if verificado_novo:
                                    await usuario_repo.update_usuario(session, novo_user.id, email_verificado=True)
                                return {"success": True, "user_id": novo_user.id, "nome": nome_novo}
                            except Exception as e:
                                return {"success": False, "error": str(e)}
                            finally:
                                await session.close()
                        
                        result = asyncio.run(_create_user())
                        if result["success"]:
                            with st.popover("✅ Sucesso!", use_container_width=True):
                                st.success(f"Usuário **{result['nome']}** cadastrado com sucesso!")
                                st.info(f"ID: {result['user_id']}")
                            st.rerun()
                        else:
                            st.error(result.get("error", "Erro ao cadastrar usuário"))

        with tab_u_editar:
            st.subheader("✏️ Editar Usuário")
            if db_users:
                user_names = [f"{u.nome} ({u.email})" for u in db_users]
                user_sel = st.selectbox("Selecione o usuário", user_names, key="cfg_user_edit_sel")
                idx = user_names.index(user_sel)
                u = db_users[idx]

                # Exibe imagem atual se existir
                from database.services.profile_image_service import get_profile_image_path, save_profile_image
                
                # Upload fora do form para pré-visualização imediata
                img_u = st.file_uploader("Nova imagem de perfil", type=["png", "jpg", "jpeg", "webp"], key=f"cfg_img_upload_{u.id}")
                
                # Mostra imagem: se fez upload mostra a nova, senão mostra a atual
                if img_u:
                    st.image(img_u, caption="Nova imagem (pré-visualização)", width=120)
                elif u.imagem_perfil:
                    img_path = get_profile_image_path(u.imagem_perfil)
                    if img_path:
                        st.image(img_path, caption="Imagem atual", width=120)
                    else:
                        st.info("Usuário sem imagem de perfil.")
                else:
                    st.info("Usuário sem imagem de perfil.")

                roles_list = ["admin", "parceiro", "cliente", "entregador", "funcionario"]
                current_role_idx = roles_list.index(u.role) if u.role in roles_list else 2
                
                with st.form("form_editar_usuario"):
                    nome_u = st.text_input("Nome", value=u.nome)
                    email_u = st.text_input("E-mail", value=u.email, disabled=True)
                    role_u = st.selectbox("Cargo", roles_list, index=current_role_idx)
                    ativo_u = st.toggle("Ativo", value=u.ativo)
                    verificado_u = st.toggle("E-mail verificado", value=u.email_verificado)
                    salvar_u = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                    if salvar_u:
                        async def _update_user():
                            session = await _db_session()
                            try:
                                update_data = {
                                    "nome": nome_u,
                                    "role": role_u,
                                    "ativo": ativo_u,
                                    "email_verificado": verificado_u,
                                }
                                img_filename = None
                                # Salva nova imagem se fornecida
                                if img_u:
                                    ext = img_u.name.rsplit(".", 1)[-1]
                                    img_filename = save_profile_image(u.email, img_u.getvalue(), f".{ext}")
                                    update_data["imagem_perfil"] = img_filename
                                
                                await usuario_repo.update_usuario(session, u.id, **update_data)
                                return {"success": True, "img_filename": img_filename}
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                                return {"success": False, "img_filename": None}
                            finally:
                                await session.close()
                        
                        result = asyncio.run(_update_user())
                        if result["success"]:
                            # Se editou o próprio usuário, atualiza o sidebar
                            if u.id == st.session_state.get("user_id"):
                                if result["img_filename"]:
                                    st.session_state.user_profile_image = result["img_filename"]
                                st.session_state.name = nome_u
                                st.session_state.primeiro_nome = nome_u.split(" ")[0] if nome_u else ""
                            with st.popover("✅ Sucesso!", use_container_width=True):
                                st.success(f"Usuário **{nome_u}** atualizado com sucesso!")
                            st.rerun()
            else:
                st.info("Nenhum usuário para editar.")

        with tab_u_deletar:
            st.subheader("🗑️ Remover Usuário")
            st.warning("⚠️ Esta ação é irreversível. O usuário será removido permanentemente.")
            if db_users:
                user_names_del = [f"{u.nome} ({u.email})" for u in db_users]
                user_del = st.selectbox("Selecione o usuário", user_names_del, key="cfg_user_del_sel")
                idx_del = user_names_del.index(user_del)
                u_del = db_users[idx_del]
                
                # Impede deleção do próprio usuário logado
                if u_del.id == st.session_state.get("user_id"):
                    st.error("❌ Você não pode excluir seu próprio usuário!")
                else:
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("🗑️ Confirmar Exclusão", use_container_width=True, type="primary", key="cfg_user_del_confirm"):
                            async def _delete_user():
                                session = await _db_session()
                                try:
                                    # Remove imagem de perfil se existir
                                    if u_del.imagem_perfil:
                                        from database.services.profile_image_service import get_profile_image_path
                                        import os as os_del
                                        img_path = get_profile_image_path(u_del.imagem_perfil)
                                        if img_path and os_del.path.exists(img_path):
                                            os_del.remove(img_path)
                                    
                                    deleted = await usuario_repo.delete_usuario(session, u_del.id)
                                    return {"success": deleted, "nome": u_del.nome}
                                except Exception as e:
                                    return {"success": False, "error": str(e)}
                                finally:
                                    await session.close()
                            
                            result = asyncio.run(_delete_user())
                            if result["success"]:
                                with st.popover("✅ Sucesso!", use_container_width=True):
                                    st.success(f"Usuário **{result['nome']}** removido com sucesso!")
                                st.rerun()
                            else:
                                st.error(result.get("error", "Erro ao remover usuário"))
                    with col_cancel:
                        if st.button("❌ Cancelar", use_container_width=True, key="cfg_user_del_cancel"):
                            st.info("Exclusão cancelada.")
            else:
                st.info("Nenhum usuário para remover.")

    st.markdown("---")
    st.caption("💡 As configurações sensíveis (API keys, webhooks) são gerenciadas via variáveis de ambiente por segurança.")
