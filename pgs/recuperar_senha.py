import streamlit as st
import secrets
from database import create_session
from database.repositories import usuario_repo
from notification import Notificador

st.title("Recuperação de Senha")

email = st.text_input("Digite seu e-mail cadastrado")

if st.button("Recuperar Senha"):
    if not email:
        st.error("Informe o e-mail cadastrado.")
    else:
        async def processar():
            session = await create_session()
            try:
                user = await usuario_repo.get_usuario_by_email(session, email)
                if not user:
                    st.error("E-mail não encontrado.")
                    return
                nova_senha = secrets.token_urlsafe(8)
                await usuario_repo.update_usuario(session, user.id, senha=nova_senha)
                notificador = Notificador()
                notificador.enviar_email_recuperacao(email, user.nome, nova_senha)
                st.success("Uma nova senha foi enviada para seu e-mail.")
            except Exception as e:
                st.error(f"Erro ao recuperar senha: {e}")
            finally:
                await session.close()
        import asyncio
        asyncio.run(processar())
