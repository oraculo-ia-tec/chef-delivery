import asyncio
import streamlit as st

from database import create_session
from database.repositories import usuario_repo
from database.services.profile_image_service import get_profile_image_path, save_profile_image


def _inject_styles():
    st.markdown(
        """
        <style>
        .conta-wrap {
            max-width: 920px;
            margin: 0 auto;
        }
        .conta-card {
            padding: 1.4rem;
            border-radius: 22px;
            background:
                radial-gradient(circle at top left, rgba(122,240,176,0.08), transparent 30%),
                linear-gradient(180deg, rgba(7,20,38,0.94), rgba(4,14,28,0.97));
            border: 1px solid rgba(122,240,176,0.14);
            box-shadow: 0 12px 28px rgba(0,0,0,0.22), 0 0 20px rgba(0,255,170,0.04);
        }
        .profile-img-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .profile-img-container img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid rgba(122,240,176,0.4);
            box-shadow: 0 0 20px rgba(0,255,170,0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def showMinhaConta():
    _inject_styles()

    st.markdown("<div class='conta-wrap'>", unsafe_allow_html=True)
    st.title("⚙️ Minha Conta")
    st.caption("Atualize seus dados cadastrais do Chef Delivery.")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Usuário não identificado.")
        st.stop()

    async def _load_user():
        session = await create_session()
        try:
            return await usuario_repo.get_usuario_by_id(session, user_id)
        finally:
            await session.close()

    try:
        usuario = asyncio.run(_load_user())
    except Exception as e:
        st.error(f"Erro ao carregar usuário: {e}")
        st.stop()

    if not usuario:
        st.warning("Usuário não encontrado.")
        st.stop()

    st.markdown("<div class='conta-card'>", unsafe_allow_html=True)

    # Upload de nova imagem (fora do form para pré-visualização imediata)
    nova_img = st.file_uploader(
        "📷 Alterar foto de perfil",
        type=["png", "jpg", "jpeg", "webp"],
        key="minha_conta_foto",
    )

    # Exibe imagem: se fez upload mostra a nova, senão mostra a atual
    col_img, col_info = st.columns([1, 2])
    with col_img:
        if nova_img:
            st.image(nova_img, caption="Nova imagem", width=120)
        elif usuario.imagem_perfil:
            img_path = get_profile_image_path(usuario.imagem_perfil)
            if img_path:
                st.image(img_path, caption="Imagem atual", width=120)
            else:
                st.markdown(
                    "<div style='width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,rgba(122,240,176,0.3),rgba(94,200,255,0.3));display:flex;align-items:center;justify-content:center;font-size:3rem;border:3px solid rgba(122,240,176,0.4);'>👤</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div style='width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,rgba(122,240,176,0.3),rgba(94,200,255,0.3));display:flex;align-items:center;justify-content:center;font-size:3rem;border:3px solid rgba(122,240,176,0.4);'>👤</div>",
                unsafe_allow_html=True,
            )
    with col_info:
        st.markdown(f"**{usuario.nome}**")
        st.caption(f"📧 {usuario.email}")
        st.caption(f"🔰 {usuario.role.capitalize()}")
        if nova_img:
            if st.button("💾 Salvar foto", key="btn_salvar_foto"):
                try:
                    ext = nova_img.name.rsplit(".", 1)[-1]
                    img_filename = save_profile_image(usuario.email, nova_img.getvalue(), f".{ext}")
                    
                    async def _update_img():
                        session = await create_session()
                        try:
                            await usuario_repo.update_usuario(session, usuario.id, imagem_perfil=img_filename)
                        finally:
                            await session.close()
                    
                    asyncio.run(_update_img())
                    st.session_state.user_profile_image = img_filename
                    with st.popover("✅ Sucesso!", use_container_width=True):
                        st.success("Foto de perfil atualizada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar foto: {e}")

    st.markdown("---")

    with st.form("form_minha_conta"):
        nome = st.text_input("Nome completo", value=usuario.nome or "")
        email = st.text_input(
            "E-mail", value=usuario.email or "", disabled=True)
        whatsapp = st.text_input(
            "WhatsApp", value=getattr(usuario, "whatsapp", "") or "")
        endereco = st.text_input(
            "Endereço", value=getattr(usuario, "endereco", "") or "")
        salvar = st.form_submit_button(
            "💾 Salvar alterações", use_container_width=True)

    if salvar:
        async def _save_user():
            session = await create_session()
            try:
                await usuario_repo.update_usuario(
                    session,
                    usuario.id,
                    nome=nome,
                    whatsapp=whatsapp,
                    endereco=endereco,
                )
                return True
            finally:
                await session.close()

        try:
            asyncio.run(_save_user())
            st.session_state.name = nome
            st.session_state.primeiro_nome = nome.split(" ")[0] if nome else ""
            with st.popover("✅ Sucesso!", use_container_width=True):
                st.success("Dados atualizados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
