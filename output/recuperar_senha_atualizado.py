import asyncio
import secrets

import streamlit as st

from database import create_session
from database.repositories import usuario_repo
from notification import Notificador


def render_recuperar_senha() -> None:
    st.markdown(
        """
        <style>
        .recover-page {
            max-width: 860px;
            margin: 2rem auto 0 auto;
            padding: 2rem;
            border-radius: 28px;
            background:
                radial-gradient(circle at top left, rgba(122,240,176,0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(94,200,255,0.10), transparent 24%),
                linear-gradient(180deg, rgba(7,20,38,0.95), rgba(4,14,28,0.98));
            border: 1px solid rgba(122,240,176,0.16);
            box-shadow: 0 18px 40px rgba(0,0,0,0.28), 0 0 24px rgba(0,255,170,0.05);
        }
        .recover-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.7rem;
            background: linear-gradient(90deg,#ffffff 0%,#7af0b0 38%,#5ec8ff 70%,#ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .recover-subtitle {
            color:#d8e4f3;
            margin-bottom:1.5rem;
            font-size:1.02rem;
        }
        .recover-label {
            display:block;
            margin:0 0 0.45rem 0.2rem;
            color:#e8f6ff;
            font-weight:700;
            font-size:0.98rem;
        }
        .recover-page .stTextInput {
            padding:0.35rem;
            border-radius:20px;
            background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.015));
            border:1px solid rgba(122,240,176,0.08);
        }
        .recover-page .stTextInput > div[data-baseweb="input"],
        .recover-page .stTextInput div[data-baseweb="base-input"] {
            background:linear-gradient(180deg, rgba(11,22,38,0.96), rgba(7,16,30,0.98)) !important;
            border:1px solid rgba(122,240,176,0.20) !important;
            border-radius:18px !important;
        }
        .recover-page .stTextInput input {
            color:#f4fbff !important;
            -webkit-text-fill-color:#f4fbff !important;
            background:transparent !important;
        }
        .recover-page .stTextInput input::placeholder {
            color:#90a9bf !important;
            -webkit-text-fill-color:#90a9bf !important;
            opacity:1 !important;
        }
        .recover-page .stButton > button {
            background: linear-gradient(135deg, rgba(122,240,176,0.18), rgba(94,200,255,0.14));
            color: #ecf4ff;
            border: 1px solid rgba(122,240,176,0.24);
            border-radius: 14px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='recover-page'>", unsafe_allow_html=True)
    st.markdown("<div class='recover-title'>Recuperação de Senha</div>", unsafe_allow_html=True)
    st.markdown("<div class='recover-subtitle'>Informe seu e-mail cadastrado para gerar uma nova senha e receber as instruções por e-mail.</div>", unsafe_allow_html=True)
    st.markdown("<div class='recover-label'>E-mail cadastrado</div>", unsafe_allow_html=True)
    email = st.text_input("Digite seu e-mail cadastrado", label_visibility="collapsed", placeholder="Digite seu e-mail")

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
                    if hasattr(notificador, "enviar_email_recuperacao"):
                        notificador.enviar_email_recuperacao(email, user.nome, nova_senha)
                    else:
                        notificador.enviar_email(
                            destino=email,
                            assunto="🔐 Chef Delivery — Recuperação de senha",
                            mensagem=f"""
                            <div style='font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:2rem;border-radius:16px;background:linear-gradient(145deg,#1a1a2e,#16213e);color:#e8f4ee;'>
                                <h2 style='color:#7af0b0;text-align:center;'>🍔 Chef Delivery</h2>
                                <p>Olá, <strong>{user.nome.split(' ')[0] if user.nome else 'cliente'}</strong>!</p>
                                <p>Sua nova senha temporária é:</p>
                                <div style='text-align:center;margin:1.5rem 0;'>
                                    <span style='font-size:1.5rem;font-weight:700;letter-spacing:2px;color:#7af0b0;background:rgba(122,240,176,0.1);padding:0.8rem 1.2rem;border-radius:12px;border:2px solid rgba(122,240,176,0.3);'>
                                        {nova_senha}
                                    </span>
                                </div>
                                <p style='font-size:0.9rem;color:#c0d8e8;'>Ao entrar no sistema, altere sua senha imediatamente.</p>
                            </div>
                            """,
                        )
                    st.success("Uma nova senha foi enviada para seu e-mail.")
                except Exception as e:
                    st.error(f"Erro ao recuperar senha: {e}")
                finally:
                    await session.close()
            asyncio.run(processar())

    if st.button("Voltar para login", key="btn_voltar_login"):
        try:
            del st.query_params["recuperar-senha"]
        except Exception:
            st.query_params.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def showRecuperarSenha() -> None:
    render_recuperar_senha()


def main() -> None:
    render_recuperar_senha()
