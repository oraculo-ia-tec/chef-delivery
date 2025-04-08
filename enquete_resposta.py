import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import requests
import pandas as pd
from key_config import DATABASE_URL, URL_DJANGO_ENQUETE


def verificar_usuario(username: str, password: str) -> Optional[Dict]:
    """Verifica credenciais do usuário no banco de dados."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            query = text("SELECT username, password, role FROM oraculo_user WHERE username = :username")
            result = connection.execute(query, {"username": username}).fetchone()

            if result:
                return {'username': result[0], 'role': result[2]}
        return None
    except Exception as e:
        st.error(f"Erro ao verificar usuário: {str(e)}")
        return None


def obter_roles() -> List[str]:
    """Obtém os tipos de papéis disponíveis para direcionamento da enquete."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            query = text("SELECT DISTINCT role FROM oraculo_user")
            roles = connection.execute(query).fetchall()
            return [role[0] for role in roles]
    except Exception as e:
        st.error(f"Erro ao buscar roles: {str(e)}")
        return []


def obter_enquetes() -> List[Dict]:
    """Recupera todas as enquetes cadastradas no banco de dados."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            query = text("""
                SELECT titulo, descricao, data_inicio, data_fim, ativo 
                FROM oraculo_enquete 
                ORDER BY created_dt DESC
            """)
            enquetes = connection.execute(query).fetchall()

            return [{
                'Título': e[0],
                'Descrição': e[1],
                'Data de Início': e[2].strftime('%d/%m/%Y %H:%M:%S'),
                'Data de Fim': e[3].strftime('%d/%m/%Y %H:%M:%S'),
                'Ativo': 'Sim' if e[4] else 'Não'
            } for e in enquetes]
    except Exception as e:
        st.error(f"Erro ao buscar enquetes: {str(e)}")
        return []


def validate_poll_dates(data_inicio: datetime, data_fim: datetime) -> bool:
    """Valida as datas da enquete."""
    now = datetime.now()
    if data_inicio < now:
        st.error("A data de início não pode ser anterior à data atual.")
        return False
    if data_fim <= data_inicio:
        st.error("A data de fim deve ser posterior à data de início.")
        return False
    return True


def get_users_by_roles(roles: List[str]) -> List[int]:
    """Obtém os IDs dos usuários com base nos papéis selecionados."""
    try:
        # Removendo barras extras e garantindo a URL correta
        url = URL_DJANGO_ENQUETE

        response = requests.get(
            url,
            params={"roles": ",".join(roles)},
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get("user_ids", [])
        else:
            st.error(f"Erro ao buscar usuários por roles: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar ao servidor: {str(e)}")
        return []


def criar_enquete():
    """Interface do Streamlit para criar enquetes."""
    st.title('Gerenciamento de Enquetes')

    roles = obter_roles()
    with st.form(key='form_enquete_criar'):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título da Enquete")
        with col2:
            direcionado_a_roles = st.multiselect(
                "Direcionado a:", options=roles, default=[], key="direcionado_enquete"
            )

        col3, col4 = st.columns(2)
        with col3:
            data_inicio = st.date_input("Data de Início", min_value=datetime.now().date())
            hora_inicio = st.time_input("Hora de Início", value=datetime.now().time())
        with col4:
            data_fim = st.date_input("Data de Fim", min_value=datetime.now().date())
            hora_fim = st.time_input("Hora de Fim", value=(datetime.now() + timedelta(hours=1)).time())

        descricao = st.text_area("Descrição da Enquete", height=100, max_chars=500)

        st.subheader("Opções de Resposta")
        col5, col6 = st.columns(2)
        opcoes = {
            'opcao1': col5.text_input("Opção 1"),
            'opcao2': col6.text_input("Opção 2"),
            'opcao3': col5.text_input("Opção 3"),
            'opcao4': col6.text_input("Opção 4")
        }

        opcoes_validas = [op for op in opcoes.values() if op.strip()]
        if opcoes_validas:
            resposta_correta = st.radio("Selecione a resposta correta:", options=opcoes_validas)

        submit_button = st.form_submit_button(label='Enviar Enquete')

        if submit_button:
            if not titulo.strip():
                st.error("O título da enquete é obrigatório.")
                return

            if len(opcoes_validas) < 2:
                st.error("A enquete deve ter pelo menos duas opções de resposta.")
                return

            data_inicio_completa = datetime.combine(data_inicio, hora_inicio)
            data_fim_completa = datetime.combine(data_fim, hora_fim)

            if not validate_poll_dates(data_inicio_completa, data_fim_completa):
                return

            # Obter IDs dos usuários pelos papéis
            direcionado_a_ids = get_users_by_roles(direcionado_a_roles)

            if not direcionado_a_ids:
                st.error("Nenhum usuário encontrado para os papéis selecionados.")
                return

            data = {
                'titulo': titulo.strip(),
                'descricao': descricao.strip(),
                'data_inicio': data_inicio_completa.isoformat(),
                'data_fim': data_fim_completa.isoformat(),
                'direcionado_a': direcionado_a_ids,  # Enviando IDs corretos
                'enquete': {key: value for key, value in opcoes.items() if value.strip()},
            }

            try:
                response = requests.post(
                    URL_DJANGO_ENQUETE,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )

                if response.status_code in [200, 201]:
                    st.success("Enquete cadastrada com sucesso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Erro ao cadastrar enquete: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao enviar dados: {str(e)}")


    st.title("Enquetes Cadastradas")
    with st.expander("Listar Enquetes"):
        enquetes = obter_enquetes()
        if enquetes:
            df_enquetes = pd.DataFrame(enquetes)
            st.dataframe(df_enquetes)
        else:
            st.info("Nenhuma enquete cadastrada ainda.")
