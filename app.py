import asyncio

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
import base64
from streamlit_option_menu import option_menu
import time

from pgs.home import showHome
from pgs.cliente_criar import showCliente
from pgs.financeiro import showFinanceiro
from pgs.pedido import showPedido
from pgs.link_pagamento import showLinks
from pgs.subcontas_criar import showParceiro
from pgs.webhooks import shoWebhooks

# --- LOAD CONFIGURATION VIA SECRETS ---
users_list = st.secrets["credentials"]["users"]

credentials = {
    'usernames': {user['username']: {
        'name': user['name'],
        'password': user['password'],
        'email': user['email'],
        'role': user.get('role', 'cliente')
    } for user in users_list}
}

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=st.secrets["cookie"]["name"],
    key=st.secrets["cookie"]["key"],
    cookie_expiry_days=st.secrets["cookie"]["expiry_days"]
)

# --- PAGE SETUP ---
authenticator.login(key='login_form')


class MultiPage:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func):
        self.pages.append({
            "title": title,
            "function": func
        })

    def run(self):
        with st.sidebar:
            pag = option_menu(
                menu_title="MENU",
                options=[page["title"] for page in self.pages],
                icons=['house-fill', 'cart-fill', 'person-fill', 'cash-stack', 'link', 'people-fill', 'code-slash'],
                menu_icon='list',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "15px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px",
                                 "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        for page in self.pages:
            if page["title"] == pag:
                asyncio.run(page["function"]())


# Verifica se o usuário está autenticado
if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
    authenticator.logout('SAIR', 'sidebar')

    # Obtenha o nome e o papel do usuário logado
    user_info = next(
        (user for user in users_list if user['username'] == st.session_state['username']), None)
    user_name = user_info['name']
    user_role = user_info.get('role', 'cliente')

    # Mensagem de boas-vindas
    st.sidebar.markdown(
        f"<h1 style='color: #FFFFFF; font-size: 24px;'>🎉 Seja bem-vindo(a), <span style='font-weight: bold;'>{user_name}</span>!!! 🎉</h1>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # Definir permissões de acesso
    permissoes = {
        "admin": ["Fazer Pedido", "Criar Cliente", "Dashboard", "Financeiro", "Link de Pagamento", "Parceiro",
                  "Webhook"],
        "parceiro": ["Fazer Pedido", "Criar Cliente"],
        "cliente": ["Fazer Pedido"]
    }

    # Mapear as funções das páginas
    pagina_func_map = {
        "Fazer Pedido": showPedido,
        "Criar Cliente": showCliente,
        "Dashboard": showHome,
        "Financeiro": showFinanceiro,
        "Link de Pagamento": showLinks,
        "Parceiro": showParceiro,
        "Webhook": shoWebhooks
    }

    # Validar o papel do usuário
    if user_role in permissoes:
        multi_page = MultiPage()

        # Adicionar páginas permitidas para o papel do usuário
        for titulo_pagina in permissoes[user_role]:
            multi_page.add_page(titulo_pagina, pagina_func_map[titulo_pagina])

        # Executar a aplicação
        multi_page.run()
    else:
        st.error("Você não tem permissão para acessar esta aplicação.")
else:
    st.info("Insira seu usuário e senha para acessar o Chef Delivery.")