import streamlit as st

# Página Home moderna para o Chef Delivery
def showHome():
    st.markdown("""
        <style>
        .card-container {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            justify-content: center;
            margin-top: 2rem;
        }
        .card {
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(2,171,33,0.15);
            padding: 2rem;
            width: 320px;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: box-shadow 0.2s;
        }
        .card:hover {
            box-shadow: 0 8px 32px rgba(2,171,33,0.25);
        }
        .card-icon {
            font-size: 3rem;
            color: #02ab21;
            margin-bottom: 1rem;
        }
        .card-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .card-desc {
            font-size: 1rem;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=120)
    st.markdown("<h1 style='color:#02ab21; text-align:center;'>Bem-vindo ao Chef Delivery!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>O melhor da gastronomia na sua casa, com agilidade e qualidade!</h3>", unsafe_allow_html=True)

    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('''
        <div class="card">
            <div class="card-icon">🍽️</div>
            <div class="card-title">Variedade de Pratos</div>
            <div class="card-desc">Escolha entre carnes nobres, acompanhamentos e sobremesas exclusivas.</div>
        </div>
        <div class="card">
            <div class="card-icon">⏱️</div>
            <div class="card-title">Entrega Rápida</div>
            <div class="card-desc">Receba seu pedido em minutos, com rastreamento em tempo real.</div>
        </div>
        <div class="card">
            <div class="card-icon">🤖</div>
            <div class="card-title">Atendimento Inteligente</div>
            <div class="card-desc">Nosso chatbot ChefBot tira dúvidas e facilita seu pedido 24h.</div>
        </div>
        <div class="card">
            <div class="card-icon">💳</div>
            <div class="card-title">Pagamento Seguro</div>
            <div class="card-desc">Diversas opções de pagamento, com total segurança e praticidade.</div>
        </div>
        <div class="card">
            <div class="card-icon">⭐</div>
            <div class="card-title">Avaliações 5 Estrelas</div>
            <div class="card-desc">Clientes satisfeitos recomendam o Chef Delivery!</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br><center><b>Faça seu pedido agora e descubra uma nova experiência gastronômica!</b></center>", unsafe_allow_html=True)
