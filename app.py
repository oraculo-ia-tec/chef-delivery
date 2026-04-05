import asyncio
import base64
import functools
import inspect
import os
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st
from streamlit_option_menu import option_menu

load_dotenv()

st.set_page_config(
    page_title="Chef Delivery",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inicializa session_state de autenticação ──
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None


def _do_login(email: str, password: str) -> bool:
    """Autentica contra o banco de dados e atualiza session_state."""
    import asyncio as _aio
    from database import create_session as _db_session
    from database.services.auth_service import authenticate_usuario

    async def _auth():
        session = await _db_session()
        try:
            usuario = await authenticate_usuario(session, email, password)
            return usuario
        finally:
            await session.close()

    usuario = _aio.run(_auth())
    if usuario is None:
        return False
    if not usuario.email_verificado:
        st.error("📧 E-mail ainda não verificado. Verifique sua caixa de entrada.")
        return False
    st.session_state.authentication_status = True
    st.session_state.username = usuario.email
    st.session_state.name = usuario.nome
    st.session_state.primeiro_nome = usuario.nome.split(" ")[0] if usuario.nome else ""
    st.session_state.user_role = usuario.role
    st.session_state.user_id = usuario.id
    return True


def _do_logout():
    """Limpa session_state de autenticação."""
    st.session_state.authentication_status = False
    st.session_state.username = None
    st.session_state.name = ""
    st.session_state.primeiro_nome = ""
    st.session_state.user_role = None
    st.session_state.user_id = None


@st.cache_data(show_spinner=False)
def build_local_image_data_uri(relative_path: str) -> str:
    image_path = Path(__file__).resolve().parent / relative_path
    if not image_path.exists():
        return ""

    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    suffix = image_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")
    return f"data:{mime_type};base64,{encoded}"


@st.cache_data(show_spinner=False)
def _build_global_css() -> str:
    """Monta o CSS global uma única vez e cacheia."""
    return """
        <style>
        html, body, [class*="css"] {
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(2,171,33,0.18), transparent 25%),
                radial-gradient(circle at top right, rgba(0,191,255,0.16), transparent 22%),
                linear-gradient(135deg, #050816 0%, #0b1220 45%, #0e1628 100%);
            color: #f5f7fb;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8,12,24,0.98) 0%, rgba(10,16,31,0.96) 100%);
            border-right: 1px solid rgba(120, 255, 182, 0.18);
            box-shadow: 0 0 35px rgba(2,171,33,0.10);
        }

        [data-testid="stSidebar"] * {
            color: #f3f7ff;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .hero-wrap {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 2.6rem 2.2rem;
            background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(120,255,182,0.18);
            box-shadow:
                0 0 0 1px rgba(0,255,170,0.04) inset,
                0 0 35px rgba(0,255,170,0.10),
                0 20px 60px rgba(0,0,0,0.32);
            backdrop-filter: blur(14px);
            animation: fadeUp 0.8s ease-out;
        }

        .top-image {
            display: flex;
            justify-content: center;
            margin-bottom: 1.2rem;
            animation: floaty 3.6s ease-in-out infinite;
        }

        .top-image img {
              width: clamp(150px, 16vw, 210px);
            border-radius: 50%;
              border: 3px solid rgba(120,255,182,0.35);
              box-shadow: 0 0 32px rgba(0,255,170,0.28);
        }

        .eyebrow {
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.20rem;
            font-size: 0.78rem;
            color: #9be9bc;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            line-height: 1.08;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #ffffff 0%, #7af0b0 38%, #5ec8ff 70%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-subtitle {
            max-width: 950px;
            margin: 0 auto 1.5rem auto;
            text-align: center;
            color: #d8e4f3;
            font-size: 1.08rem;
            line-height: 1.8;
        }

        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.8rem;
            margin-top: 1.4rem;
        }

        .hero-showcase {
            display: flex;
            justify-content: center;
            margin-top: 1.8rem;
        }

        .meat-stage {
            position: relative;
            width: min(760px, 100%);
            min-height: 230px;
            padding: 1.3rem;
            border-radius: 26px;
            overflow: hidden;
            background:
                radial-gradient(circle at 15% 20%, rgba(255, 114, 87, 0.20), transparent 30%),
                radial-gradient(circle at 85% 25%, rgba(255, 192, 72, 0.16), transparent 28%),
                linear-gradient(145deg, rgba(17,24,39,0.95), rgba(10,16,31,0.88));
            border: 1px solid rgba(255, 161, 122, 0.18);
            box-shadow: 0 18px 45px rgba(0,0,0,0.30), 0 0 28px rgba(255, 110, 84, 0.10);
        }

        .meat-stage::before {
            content: "";
            position: absolute;
            inset: auto -8% -42% -8%;
            height: 140px;
            background: radial-gradient(circle, rgba(255, 112, 67, 0.30), transparent 62%);
            filter: blur(18px);
        }

        .ticker-row {
            display: flex;
            justify-content: space-between;
            gap: 0.8rem;
            align-items: center;
            margin-bottom: 1rem;
            font-size: 0.86rem;
            color: #ffe6cf;
        }

        .ticker-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255, 173, 124, 0.18);
        }

        .signal-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #7af0b0;
            box-shadow: 0 0 12px rgba(122,240,176,0.75);
            animation: pulseDot 1.6s ease-in-out infinite;
        }

        .meat-grid {
            position: relative;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            z-index: 1;
        }

        .meat-card {
            position: relative;
            padding: 1rem;
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
            border: 1px solid rgba(255, 170, 125, 0.16);
            box-shadow: 0 14px 32px rgba(0,0,0,0.22);
            animation: meatFloat 4.2s ease-in-out infinite;
        }

        .meat-card:nth-child(2) {
            animation-delay: 0.35s;
        }

        .meat-card:nth-child(3) {
            animation-delay: 0.7s;
        }

        .meat-emoji {
            font-size: 2rem;
            margin-bottom: 0.55rem;
        }

        .meat-name {
            font-size: 1.02rem;
            font-weight: 700;
            color: #fff5ee;
            margin-bottom: 0.35rem;
        }

        .meat-copy {
            font-size: 0.9rem;
            line-height: 1.5;
            color: #f0ddd3;
            min-height: 44px;
        }

        .meat-price {
            display: inline-block;
            margin-top: 0.8rem;
            padding: 0.42rem 0.72rem;
            border-radius: 999px;
            background: rgba(122,240,176,0.12);
            border: 1px solid rgba(122,240,176,0.22);
            color: #dff8ea;
            font-size: 0.88rem;
            font-weight: 600;
        }

        .sales-ribbon {
            position: absolute;
            right: 1rem;
            bottom: 1rem;
            display: inline-flex;
            gap: 0.55rem;
            align-items: center;
            padding: 0.6rem 0.85rem;
            border-radius: 16px;
            background: rgba(8, 12, 24, 0.74);
            border: 1px solid rgba(255, 163, 122, 0.18);
            color: #ffe9d6;
            font-size: 0.88rem;
            z-index: 2;
            animation: ribbonSlide 5s ease-in-out infinite;
        }

        .sales-ribbon strong {
            color: #7af0b0;
        }

        .hero-badge {
            padding: 0.72rem 1rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(120,255,182,0.14);
            color: #e9f6ff;
            font-size: 0.92rem;
            box-shadow: 0 0 18px rgba(0,255,170,0.05);
        }

        .section-title {
            margin: 2rem 0 1rem 0;
            text-align: center;
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ffffff, #8ee7ff, #7af0b0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .section-text {
            text-align: center;
            color: #d4e1ef;
            font-size: 1rem;
            max-width: 900px;
            margin: 0 auto 1.6rem auto;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.2rem;
            margin-top: 1.1rem;
        }

        .glass-card {
            position: relative;
            overflow: hidden;
            min-height: 220px;
            padding: 1.4rem;
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border: 1px solid rgba(126, 255, 197, 0.18);
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.03) inset,
                0 0 28px rgba(0,255,170,0.08),
                0 16px 34px rgba(0,0,0,0.25);
            transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;
            animation: fadeUp 0.7s ease-out;
        }

        .glass-card:hover {
            transform: translateY(-8px) scale(1.01);
            border-color: rgba(126, 255, 197, 0.35);
            box-shadow:
                0 0 0 1px rgba(126,255,197,0.08) inset,
                0 0 34px rgba(0,255,170,0.14),
                0 20px 45px rgba(0,0,0,0.33);
        }

        .glass-card::after {
            content: "";
            position: absolute;
            top: 0;
            left: -120%;
            width: 120%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
            transition: left 0.8s ease;
        }

        .glass-card:hover::after {
            left: 120%;
        }

        .card-icon {
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 18px;
            margin-bottom: 1rem;
            font-size: 1.9rem;
            background: linear-gradient(135deg, rgba(122,240,176,0.16), rgba(94,200,255,0.16));
            border: 1px solid rgba(126,255,197,0.20);
            box-shadow: 0 0 20px rgba(0,255,170,0.08);
        }

        .card-title {
            font-size: 1.18rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
            color: #ffffff;
        }

        .card-desc {
            color: #d7e4f2;
            font-size: 0.96rem;
            line-height: 1.7;
        }

        .metrics-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-top: 1.8rem;
        }

        .metric-box {
            text-align: center;
            padding: 1.3rem 1rem;
            border-radius: 22px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(126,255,197,0.16);
            box-shadow: 0 0 20px rgba(0,255,170,0.06);
        }

        .metric-number {
            font-size: 1.9rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
            background: linear-gradient(90deg, #ffffff, #7af0b0, #8ee7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .metric-label {
            color: #d2deea;
            font-size: 0.94rem;
        }

        .login-note {
            margin-top: 1rem;
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: rgba(122,240,176,0.08);
            border: 1px solid rgba(122,240,176,0.14);
            color: #dff8ea;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        /* ── Sidebar Auth Buttons ── */
        .sidebar-auth-title {
            text-align: center;
            font-size: 1.15rem;
            font-weight: 700;
            margin: 0.6rem 0 1rem 0;
            background: linear-gradient(90deg, #ffffff 10%, #7af0b0 50%, #5ec8ff 90%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeUp 0.6s ease-out;
        }

        .auth-btn-row {
            display: flex;
            gap: 0.55rem;
            margin-bottom: 1.2rem;
            animation: fadeUp 0.5s ease-out;
        }

        .auth-btn-row button {
            flex: 1;
            padding: 0.62rem 0;
            border-radius: 12px;
            font-size: 0.92rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.35s ease;
            border: 1px solid rgba(120,255,182,0.22);
            letter-spacing: 0.02rem;
        }

        [data-testid="stSidebar"] [data-testid="stColumns"] button {
            width: 100%;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 0.6rem 0.2rem !important;
            transition: all 0.35s ease !important;
        }

        [data-testid="stSidebar"] [data-testid="stColumns"] > div:first-child button {
            background: linear-gradient(135deg, rgba(2,171,33,0.35), rgba(0,191,255,0.20)) !important;
            border: 1px solid rgba(120,255,182,0.30) !important;
            color: #fff !important;
            box-shadow: 0 0 18px rgba(0,255,170,0.12) !important;
        }

        [data-testid="stSidebar"] [data-testid="stColumns"] > div:first-child button:hover {
            background: linear-gradient(135deg, rgba(2,171,33,0.55), rgba(0,191,255,0.32)) !important;
            box-shadow: 0 0 28px rgba(0,255,170,0.25) !important;
            transform: translateY(-2px) !important;
        }

        [data-testid="stSidebar"] [data-testid="stColumns"] > div:last-child button {
            background: linear-gradient(135deg, rgba(94,200,255,0.18), rgba(167,139,250,0.15)) !important;
            border: 1px solid rgba(94,200,255,0.28) !important;
            color: #fff !important;
            box-shadow: 0 0 18px rgba(94,200,255,0.10) !important;
        }

        [data-testid="stSidebar"] [data-testid="stColumns"] > div:last-child button:hover {
            background: linear-gradient(135deg, rgba(94,200,255,0.35), rgba(167,139,250,0.28)) !important;
            box-shadow: 0 0 28px rgba(94,200,255,0.22) !important;
            transform: translateY(-2px) !important;
        }

        /* ── Sidebar Form Borders ── */
        .sidebar-form-box {
            position: relative;
            padding: 1.3rem 1rem;
            margin: 0.6rem 0;
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            border: 1px solid rgba(120,255,182,0.22);
            box-shadow:
                0 0 25px rgba(0,255,170,0.06),
                0 12px 35px rgba(0,0,0,0.22);
            animation: fadeUp 0.6s ease-out;
        }

        .sidebar-form-box::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            border-radius: 18px 18px 0 0;
            background: linear-gradient(90deg, #7af0b0, #5ec8ff, #a78bfa);
            opacity: 0.7;
        }

        .sidebar-form-box.signup-box {
            border-color: rgba(94,200,255,0.25);
            box-shadow:
                0 0 25px rgba(94,200,255,0.08),
                0 12px 35px rgba(0,0,0,0.22);
        }

        .sidebar-form-box.signup-box::before {
            background: linear-gradient(90deg, #5ec8ff, #a78bfa, #7af0b0);
        }

        .form-header {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.8rem;
            font-size: 1.05rem;
            font-weight: 700;
            color: #e8f5ff;
        }

        .form-header-icon {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            font-size: 1.1rem;
            background: linear-gradient(135deg, rgba(122,240,176,0.18), rgba(94,200,255,0.18));
            border: 1px solid rgba(126,255,197,0.20);
        }

        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 18px rgba(0,255,170,0.10); }
            50%      { box-shadow: 0 0 28px rgba(0,255,170,0.22); }
        }

        .sidebar-form-box {
            animation: fadeUp 0.6s ease-out, glowPulse 3s ease-in-out infinite;
        }

        @keyframes fadeUp {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }

        @keyframes shine {
            0% {transform: translateX(-100%);}
            100% {transform: translateX(100%);}
        }

        @keyframes floaty {
            0%, 100% {transform: translateY(0px);}
            50% {transform: translateY(-8px);}
        }

        @keyframes pulseDot {
            0%, 100% {transform: scale(1); opacity: 1;}
            50% {transform: scale(1.35); opacity: 0.72;}
        }

        @keyframes meatFloat {
            0%, 100% {transform: translateY(0px);}
            50% {transform: translateY(-10px);}
        }

        @keyframes ribbonSlide {
            0%, 100% {transform: translateX(0px);}
            50% {transform: translateX(-10px);}
        }

        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.15rem;
            }
            .hero-wrap {
                padding: 1.6rem 1rem;
            }
            .top-image img {
                width: 160px;
            }
            .meat-grid {
                grid-template-columns: 1fr;
            }
            .sales-ribbon {
                position: static;
                margin-top: 1rem;
                justify-content: center;
            }
        }
        </style>
        """


def inject_global_style() -> None:
    st.markdown(_build_global_css(), unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _build_hero_html(image_data_uri: str) -> str:
    """Monta o HTML do hero da landing page uma única vez."""
    return f"""
        <div class="hero-wrap">
            <div class="top-image">
                <img src="{image_data_uri}" alt="Chef Delivery">
            </div>
            <div class="eyebrow">Atendimento inteligente para vendas online</div>
            <div class="hero-title">Chef Delivery acelera pedidos, reduz custos e aumenta suas vendas</div>
            <div class="hero-subtitle">
                Transforme o atendimento em uma operação mais rápida, escalável e lucrativa com um fluxo digital que apresenta produtos,
                organiza pedidos, melhora a experiência do cliente e prepara sua operação para pagamentos, automações e crescimento contínuo.
            </div>
            <div class="hero-badges">
                <div class="hero-badge">Atendimento com mais agilidade</div>
                <div class="hero-badge">Escalabilidade comercial</div>
                <div class="hero-badge">Menos custo operacional</div>
                <div class="hero-badge">Mais conversão em vendas</div>
            </div>
            <div class="hero-showcase">
                <div class="meat-stage">
                    <div class="ticker-row">
                        <div class="ticker-badge"><span class="signal-dot"></span> Vitrine inteligente para açougue e churrasco</div>
                        <div class="ticker-badge">Pedidos guiados em tempo real</div>
                    </div>
                    <div class="meat-grid">
                        <div class="meat-card">
                            <div class="meat-emoji">🥩</div>
                            <div class="meat-name">Picanha Premium</div>
                            <div class="meat-copy">Destaque cortes nobres, gere desejo e conduza o cliente até o fechamento com rapidez.</div>
                            <div class="meat-price">Oferta sugerida • R$ 79,90/kg</div>
                        </div>
                        <div class="meat-card">
                            <div class="meat-emoji">🔥</div>
                            <div class="meat-name">Kit Churrasco</div>
                            <div class="meat-copy">Combine carnes, acompanhamentos e adicionais em uma experiência de compra mais visual.</div>
                            <div class="meat-price">Venda combinada • ticket maior</div>
                        </div>
                        <div class="meat-card">
                            <div class="meat-emoji">🛒</div>
                            <div class="meat-name">Pedido Acelerado</div>
                            <div class="meat-copy">Capte preferências, peso, cortes e observações do cliente sem travar o atendimento.</div>
                            <div class="meat-price">Fluxo otimizado • menos atrito</div>
                        </div>
                    </div>
                    <div class="sales-ribbon">Mais destaque para cortes, <strong>mais conversão no pedido</strong></div>
                </div>
            </div>
        </div>
        """


@st.cache_data(show_spinner=False)
def _build_cards_html() -> str:
    return """
        <div class="section-title">Benefícios e vantagens do Chef Delivery</div>
        <div class="section-text">A plataforma foi pensada para unir atendimento, apresentação comercial e organização do pedido em uma experiência moderna, clara e preparada para crescer com o seu negócio.</div>
        <div class="cards-grid">
            <div class="glass-card">
                <div class="card-icon">🚀</div>
                <div class="card-title">Escalabilidade no atendimento</div>
                <div class="card-desc">Atenda mais clientes ao mesmo tempo com um fluxo padronizado, rápido e consistente, sem depender de respostas manuais para cada nova conversa.</div>
            </div>
            <div class="glass-card">
                <div class="card-icon">💰</div>
                <div class="card-title">Redução de custos</div>
                <div class="card-desc">Diminua retrabalho, erros de comunicação e tempo gasto com atendimento repetitivo, criando uma operação comercial mais enxuta e eficiente.</div>
            </div>
            <div class="glass-card">
                <div class="card-icon">📈</div>
                <div class="card-title">Aumento nas vendas</div>
                <div class="card-desc">Apresente ofertas com mais clareza, conduza o cliente até a decisão de compra e eleve a taxa de conversão com um atendimento orientado para fechamento.</div>
            </div>
            <div class="glass-card">
                <div class="card-icon">🤖</div>
                <div class="card-title">Atendimento inteligente</div>
                <div class="card-desc">O Chef Delivery ajuda o cliente a escolher produtos, cortes, quantidades e adicionais, melhorando a experiência e acelerando o pedido.</div>
            </div>
            <div class="glass-card">
                <div class="card-icon">⏱️</div>
                <div class="card-title">Mais velocidade operacional</div>
                <div class="card-desc">Centralize dados do cliente, pedido e observações em um único fluxo, reduzindo tempo de resposta e preparando a operação para entrega e pagamento.</div>
            </div>
            <div class="glass-card">
                <div class="card-icon">🛡️</div>
                <div class="card-title">Base pronta para crescer</div>
                <div class="card-desc">Estruture sua operação para integrar pagamentos, automações, dashboards, webhooks e novos canais de atendimento sem refazer toda a aplicação.</div>
            </div>
        </div>
        """


@st.cache_data(show_spinner=False)
def _build_metrics_html() -> str:
    return """
        <div class="section-title">Resultados que impactam o negócio</div>
        <div class="section-text">O Chef Delivery não é apenas uma vitrine digital. Ele atua como uma camada estratégica para vender melhor, atender com qualidade e escalar com organização.</div>
        <div class="metrics-row">
            <div class="metric-box">
                <div class="metric-number">24/7</div>
                <div class="metric-label">Capacidade de atendimento contínuo</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">+Agilidade</div>
                <div class="metric-label">Menor tempo entre dúvida e fechamento</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">+Conversão</div>
                <div class="metric-label">Mais pedidos concluídos com clareza</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">+Controle</div>
                <div class="metric-label">Dados organizados para operar e expandir</div>
            </div>
        </div>
        """


def render_landing_page() -> None:
    image_uri = build_local_image_data_uri("src/img/perfil.png")
    st.markdown(_build_hero_html(image_uri), unsafe_allow_html=True)
    st.markdown(_build_cards_html(), unsafe_allow_html=True)
    st.markdown(_build_metrics_html(), unsafe_allow_html=True)


class MultiPage:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func, icon="circle-fill"):
        self.pages.append({"title": title, "function": func, "icon": icon})

    def run(self):
        with st.sidebar:
            selected = option_menu(
                menu_title="MENU",
                options=[page["title"] for page in self.pages],
                icons=[page["icon"] for page in self.pages],
                menu_icon="list",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#7af0b0", "font-size": "16px"},
                    "nav-link": {
                        "color": "#ecf4ff",
                        "font-size": "17px",
                        "text-align": "left",
                        "margin": "4px 0",
                        "border-radius": "10px",
                        "--hover-color": "rgba(122,240,176,0.10)",
                    },
                    "nav-link-selected": {
                        "background-color": "rgba(2,171,33,0.28)",
                        "color": "white",
                    },
                },
            )

        for page in self.pages:
            if page["title"] == selected:
                result = page["function"]()
                if inspect.isawaitable(result):
                    asyncio.run(result)
                break


inject_global_style()

with st.sidebar:
    st.markdown(
        '<div class="sidebar-auth-title">🍔 Chef Delivery</div>',
        unsafe_allow_html=True,
    )

    # ── Inicializar estado do formulário ──
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    col_login, col_signup = st.columns(2)
    with col_login:
        if st.button("🔑 Login", use_container_width=True, key="btn_login"):
            st.session_state.auth_mode = "login"
    with col_signup:
        if st.button("📝 Criar Conta", use_container_width=True, key="btn_signup"):
            st.session_state.auth_mode = "signup"

    if st.session_state.auth_mode == "login":
        st.markdown(
            '<div class="sidebar-form-box">'
            '<div class="form-header"><span class="form-header-icon">🔑</span> Acesso ao sistema</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            login_email = st.text_input("E-mail")
            login_senha = st.text_input("Senha", type="password")
            login_submit = st.form_submit_button(
                "🔑 Entrar", use_container_width=True,
            )
            if login_submit:
                if not login_email or not login_senha:
                    st.error("Preencha e-mail e senha.")
                else:
                    if _do_login(login_email, login_senha):
                        st.rerun()
                    else:
                        if st.session_state.authentication_status is False:
                            st.error("❌ E-mail ou senha incorretos.")
        st.markdown(
            "<div class='login-note'>Faça login para acessar pedidos, dashboard e recursos inteligentes do Chef Delivery.</div>",
            unsafe_allow_html=True,
        )
    else:
        # ── Estado de verificação ──
        if "verificacao_pendente" not in st.session_state:
            st.session_state.verificacao_pendente = False
        if "codigo_verificacao" not in st.session_state:
            st.session_state.codigo_verificacao = None
        if "email_verificacao" not in st.session_state:
            st.session_state.email_verificacao = None
        if "usuario_id_verificacao" not in st.session_state:
            st.session_state.usuario_id_verificacao = None

        if not st.session_state.verificacao_pendente:
            # ── Formulário de cadastro ──
            st.markdown(
                '<div class="sidebar-form-box signup-box">'
                '<div class="form-header"><span class="form-header-icon">📝</span> Criar nova conta</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            # Upload fora do form (limitação Streamlit)
            foto_signup = st.file_uploader(
                "📷 Foto de perfil",
                type=["png", "jpg", "jpeg", "webp"],
                key="signup_foto",
            )
            if foto_signup:
                st.image(foto_signup, width=80, caption=foto_signup.name)

            with st.form("signup_form", clear_on_submit=True):
                nome_signup = st.text_input("Nome completo")
                email_signup = st.text_input("E-mail")
                whatsapp_signup = st.text_input("WhatsApp")
                senha_signup = st.text_input("Senha", type="password")
                senha_confirm = st.text_input("Confirmar senha", type="password")
                submitted = st.form_submit_button(
                    "✅ Criar conta", use_container_width=True,
                )

                if submitted:
                    if not all([nome_signup, email_signup, whatsapp_signup,
                                senha_signup]):
                        st.error("Preencha todos os campos obrigatórios.")
                    elif senha_signup != senha_confirm:
                        st.error("As senhas não coincidem.")
                    else:
                        import asyncio as _aio
                        import secrets as _secrets
                        from database.services.auth_service import register_usuario
                        from database.services.profile_image_service import (
                            save_profile_image,
                        )
                        from database import create_session as _db_session
                        from notification import Notificador

                        async def _do_register():
                            img_filename = None
                            if foto_signup:
                                ext = foto_signup.name.rsplit(".", 1)[-1]
                                img_filename = save_profile_image(
                                    email_signup, foto_signup.getvalue(), f".{ext}"
                                )
                            session = await _db_session()
                            try:
                                usuario = await register_usuario(
                                    session,
                                    nome=nome_signup,
                                    email=email_signup,
                                    whatsapp=whatsapp_signup,
                                    password=senha_signup,
                                    role="cliente",
                                    imagem_perfil=img_filename,
                                )
                                return usuario.id
                            except Exception as e:
                                st.error(f"Erro ao criar conta: {e}")
                                return None
                            finally:
                                await session.close()

                        usuario_id = _aio.run(_do_register())
                        if usuario_id:
                            codigo = str(_secrets.randbelow(900000) + 100000)
                            st.session_state.codigo_verificacao = codigo
                            st.session_state.email_verificacao = email_signup
                            st.session_state.usuario_id_verificacao = usuario_id

                            try:
                                notificador = Notificador()
                                notificador.enviar_email(
                                    destino=email_signup,
                                    assunto="🔐 Chef Delivery — Código de verificação",
                                    mensagem=f"""
                                    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;
                                        padding:2rem;border-radius:16px;
                                        background:linear-gradient(145deg,#1a1a2e,#16213e);color:#e8f4ee;">
                                        <h2 style="color:#7af0b0;text-align:center;">🍔 Chef Delivery</h2>
                                        <p>Olá, <strong>{nome_signup.split(' ')[0]}</strong>!</p>
                                        <p>Seu código de verificação é:</p>
                                        <div style="text-align:center;margin:1.5rem 0;">
                                            <span style="font-size:2rem;font-weight:700;letter-spacing:8px;
                                                color:#7af0b0;background:rgba(122,240,176,0.1);
                                                padding:0.8rem 1.5rem;border-radius:12px;
                                                border:2px solid rgba(122,240,176,0.3);">
                                                {codigo}
                                            </span>
                                        </div>
                                        <p style="font-size:0.9rem;color:#c0d8e8;">
                                            Digite este código no campo de verificação para ativar sua conta.
                                        </p>
                                        <hr style="border-color:rgba(122,240,176,0.15);margin:1.5rem 0;">
                                        <p style="font-size:0.78rem;color:#888;">
                                            Se você não solicitou este cadastro, ignore este e-mail.
                                        </p>
                                    </div>
                                    """,
                                )
                                st.session_state.verificacao_pendente = True
                                st.rerun()
                            except Exception as e:
                                st.warning(
                                    f"Conta criada, mas não foi possível enviar o e-mail de verificação: {e}"
                                )
                                st.session_state.auth_mode = "login"

            st.markdown(
                "<div class='login-note'>Após criar sua conta, clique em <strong>Login</strong> para acessar o sistema.</div>",
                unsafe_allow_html=True,
            )
        else:
            # ── Formulário de verificação de e-mail ──
            st.markdown(
                '<div class="sidebar-form-box signup-box">'
                '<div class="form-header"><span class="form-header-icon">🔐</span> Verificar e-mail</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.info(
                f"📧 Código enviado para **{st.session_state.email_verificacao}**"
            )

            with st.form("verify_form"):
                codigo_input = st.text_input(
                    "Digite o código de 6 dígitos",
                    max_chars=6,
                    placeholder="000000",
                )
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    verificar = st.form_submit_button(
                        "✅ Verificar", use_container_width=True,
                    )
                with col_v2:
                    cancelar = st.form_submit_button(
                        "❌ Cancelar", use_container_width=True,
                    )

                if verificar:
                    if codigo_input == st.session_state.codigo_verificacao:
                        import asyncio as _aio
                        from database import create_session as _db_session
                        from database.repositories import usuario_repo

                        async def _verificar_email():
                            session = await _db_session()
                            try:
                                await usuario_repo.update_usuario(
                                    session,
                                    st.session_state.usuario_id_verificacao,
                                    email_verificado=True,
                                )
                                return True
                            except Exception as e:
                                st.error(f"Erro ao verificar: {e}")
                                return False
                            finally:
                                await session.close()

                        ok = _aio.run(_verificar_email())
                        if ok:
                            st.success(
                                "✅ E-mail verificado com sucesso! Use o Login para entrar."
                            )
                            st.session_state.verificacao_pendente = False
                            st.session_state.codigo_verificacao = None
                            st.session_state.email_verificacao = None
                            st.session_state.usuario_id_verificacao = None
                            st.session_state.auth_mode = "login"
                            st.rerun()
                    else:
                        st.error("❌ Código incorreto. Tente novamente.")

                if cancelar:
                    st.session_state.verificacao_pendente = False
                    st.session_state.codigo_verificacao = None
                    st.session_state.email_verificacao = None
                    st.session_state.usuario_id_verificacao = None
                    st.session_state.auth_mode = "signup"
                    st.rerun()


if st.session_state.get("authentication_status"):
    with st.sidebar:
        if st.button("🚪 SAIR", use_container_width=True, key="btn_logout"):
            _do_logout()
            st.rerun()

    user_name = st.session_state.get("name", "")
    user_role = st.session_state.get("user_role", "cliente")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div class='login-note'>✅ Usuário conectado: <strong>{user_name}</strong></div>",
        unsafe_allow_html=True,
    )

    mp = MultiPage()

    from pgs.pedido import showPedido
    mp.add_page("Chef Delivery", showPedido, "cart-fill")
    if user_role == "admin":
        from pgs.dashboard import showDashboard
        mp.add_page("Dashboard", showDashboard, "bar-chart-fill")
    if user_role in {"admin", "parceiro"}:
        from pgs.teste_api import showTesteApi
        mp.add_page("Teste da API", showTesteApi, "bug-fill")
        from pgs.clientes import showClientes
        mp.add_page("Clientes", showClientes, "people-fill")
        from pgs.pagamentos import showPagamentos
        mp.add_page("Pagamentos", showPagamentos, "credit-card-fill")
        from pgs.produtos import showProdutos
        mp.add_page("Produtos", showProdutos, "box-seam-fill")
        from pgs.preparacao import showPreparacao
        mp.add_page("Preparação", showPreparacao, "fire")
        from pgs.entregador import showEntregador
        mp.add_page("Entregador", showEntregador, "bicycle")
    if user_role == "admin":
        from pgs.parceiros import showParceiros
        mp.add_page("Parceiros", showParceiros, "handshake")
        from pgs.configuracao_page import showConfiguracao
        mp.add_page("Configuração", showConfiguracao, "gear-fill")

    if mp.pages:
        mp.run()
    else:
        st.warning("Nenhuma página disponível para seu perfil.")
else:
    render_landing_page()
