import streamlit as st
from streamlit_authenticator import Authenticate
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decouple import config
from typing import Dict
from datetime import datetime

# Importação das views
from mestre_biblia import show_mestre_biblia
from conta_loja import showConta
from views.cliente_criar import showMembro
from views.financeiro import showFinanceiro
from views.link_pagamento import show_pagamento_links
from produtos_V2 import cadastrar_produto
from views.membro_v3 import showMembro
from novo_membro import show_novo_membro
from loja import criar_loja, show_loja
from views.parceiro import showParceiro
from postar import postar_face_insta
from home_teste import showHomeTeste
from enquete_resposta import criar_enquete, exibir_enquetes
from resposta_enquete import resposta_enquete
from eventos import show_evento
from departamentos import show_departamentos
from cultos import cadastrar_culto
from teste_oraculo import showTeste
from dizimo_oferta import show_dizimo_oferta
from pagamentos import show_pagamentos


# Configuração do banco de dados
DATABASE_URL = config("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def obter_usuarios() -> Dict:
    """Obtém credenciais dos usuários das tabelas oraculo_user e oraculo_teste."""

    credentials = {'usernames': {}}

    try:
        with engine.connect() as connection:
            st.write("✅ Conectado ao banco de dados!")

            # Consulta para oraculo_user incluindo o nome do cargo
            query_user = text("""
                SELECT username, password, email, name, cargo_id FROM oraculo_user
            """)
            result_user = connection.execute(query_user).fetchall()

            # Consulta para oraculo_teste (caso exista)
            query_teste = text("""
                SELECT usuario AS username, password, email, cargo_id
                FROM oraculo_teste;
            """)
            result_teste = connection.execute(query_teste).fetchall()

            # Adiciona usuários de oraculo_user
            for user in result_user:
                username, password, email, name, cargo_id = user
                if username:  # Evita valores None
                    cargo_nome_query = text("SELECT name FROM oraculo_cargo WHERE id = :cargo_id")
                    cargo_nome_result = connection.execute(cargo_nome_query, {"cargo_id": cargo_id}).fetchone()
                    cargo_nome = cargo_nome_result[0] if cargo_nome_result else "Cargo Desconhecido"

                    credentials['usernames'][username] = {
                        'password': password,
                        'email': email,
                        'name': name,
                        'cargo_nome': cargo_nome
                    }

            # Adiciona usuários de oraculo_teste sem sobrescrever existentes
            for user in result_teste:
                username, password, email, cargo_id = user
                if username and username not in credentials['usernames']:
                    cargo_nome_query = text("SELECT name FROM oraculo_cargo WHERE id = :cargo_id")
                    cargo_nome_result = connection.execute(cargo_nome_query, {"cargo_id": cargo_id}).fetchone()
                    cargo_nome = cargo_nome_result[0] if cargo_nome_result else "Cargo Desconhecido"

                    credentials['usernames'][username] = {
                        'password': password,
                        'email': email,
                        'name': "Usuário Sem Nome",  # Exemplo genérico
                        'cargo_nome': cargo_nome
                    }

    except Exception as e:
        st.error(f"⚠️ Erro ao obter usuários: {e}")
        print(f"⚠️ ERRO ao obter usuários: {e}")  # Log no console

    return credentials


# --- 🔐 Autenticação ---
credentials = obter_usuarios()
authenticator = Authenticate(
    credentials=credentials,
    cookie_name=config('COOKIE_NAME'),
    key=config('COOKIE_KEY'),
    cookie_expiry_days=30
)

authenticator.login()


# Inicializa a variável logout no estado da sessão
if "logout" not in st.session_state:
    st.session_state.logout = False

# Verifica autenticação
if 'authentication_status' in st.session_state:
    if st.session_state['authentication_status']:
        user_details = credentials['usernames'].get(st.session_state['username'])
        if user_details:
            st.session_state['email'] = user_details.get('email', '')
            st.session_state['cargo'] = user_details.get('cargo_nome', '')
            st.session_state['name'] = user_details.get('name', '')

        st.sidebar.markdown(
            f"<h1 style='color: #FFFFFF; font-size: 24px;'>🎉 Seja bem-vindo(a), <span style='font-weight: bold;'>{st.session_state['name']}</span>!!! 🎉</h1>",
            unsafe_allow_html=True
        )

        with st.sidebar:
            if st.button("🚪 Sair", key="logout_button"):
                st.session_state.logout = True
                st.session_state.authentication_status = False  # Desloga o usuário
                st.rerun()  # Atualiza a página

        # Permissões de acesso
        permissao_usuario = {
            "Admin": [
                "MESTRE BIBLIA",
                "Cadastrar Membro",
                "Cadastrar Cultos",
                "Cadastrar Departamento",
                "Cadastrar Evento",
                "Cadastrar Loja",
                "Lojas",
                "Cadastrar Produto",
                "Cadastrar Enquete",
                "Responder Enquete",
                "Minha Conta",
                "Novo Membro",
                "Dízmo/Oferta",
                "Financeiro",
                "Pagamentos Asaas",
                "Link de Pagamento",
                "Cadastrar Parceiro",
                "Configurar Postagens"
            ],
            "Pastor": [
                "MESTRE BIBLIA",
                "Lojas",
                "Cadastrar Membro",
                "Responder Enquete",
                "Minha Conta"
            ],
            "Lider": [
                "MESTRE BIBLIA",
                "Lojas",
                "Cadastrar Membro",
                "Cadastrar Cultos",
                "Cadastrar Loja",
                "Cadastrar Produto",
                "Responder Enquete",
                "Cadastrar Departamento",
                "Minha Conta",
            ],
            "Colaborador": [
                "MESTRE BIBLIA",
                "Lojas",
                "Responder Enquete"
            ],
            "Membro": [
                "MESTRE BIBLIA",
                "Lojas",
                "Responder Enquete"
            ],
            "TESTAR": [
                "MESTRE BÍBLIA(teste)",
                "Lojas",
                "Responder Enquete",
            ],
            "Diácono": [
                "MESTRE BIBLIA",
                "Lojas",
                "Responder Enquete"
            ],
        }

        # Verificação das páginas permitidas
        paginas_permitidas = permissao_usuario.get(st.session_state['cargo'], [])

        st.text(f"Páginas permitidas para o cargo {st.session_state['cargo']}: {paginas_permitidas}")

        pages = {
            "MESTRE BIBLIA": show_mestre_biblia,
            "Minha Conta": showConta,
            "Cadastrar Produto": cadastrar_produto,
            "Cadastrar Membro": showMembro,
            "Novo Membro": show_novo_membro,
            "Cadastrar Loja": criar_loja,
            "Lojas": show_loja,
            "Financeiro": showFinanceiro,
            "Pagamentos Asaas": show_pagamentos,
            "Dízmo/Oferta": show_dizimo_oferta,
            "Link de Pagamento": show_pagamento_links,
            "Cadastrar Parceiro": showParceiro,
            "Configurar Postagens": postar_face_insta,
            "Cadastrar Enquete": criar_enquete,
            "Responder Enquete": exibir_enquetes,
            "Cadastrar Evento": show_evento,
            "Cadastrar Departamento": show_departamentos,
            "Cadastrar Cultos": cadastrar_culto,
            "ORÁCULO BÍBLIA": showHomeTeste,
            "MESTRE BÍBLIA(teste)": showTeste,
        }

        allowed_pages = {key: pages[key] for key in paginas_permitidas if key in pages}

        if allowed_pages:
            selected_page = st.sidebar.radio(
                "PÁGINAS:",
                list(allowed_pages.keys()),
                key='unique_page_navigation'
            )

            if selected_page == "Responder Enquete":
                exibir_enquetes(st.session_state['cargo'])  # Exibe enquetes direcionadas ao cargo
            elif selected_page in allowed_pages:
                allowed_pages[selected_page]()
    else:
        st.info("⚠️ Use seu login e senha para entrar.")
else:
    st.warning("⚠️ Por favor, faça login.")


