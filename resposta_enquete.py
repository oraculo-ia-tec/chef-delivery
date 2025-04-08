import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import List, Dict, Optional
from key_config import URL_DJANGO_ENQUETE, URL_DJANGO_RESPOSTA


def verificar_resposta_anterior(enquete_id: int, username: str) -> bool:
    """Verifica se o usuário já respondeu a enquete."""
    try:
        response = requests.get(
            URL_DJANGO_RESPOSTA,
            params={'enquete_id': enquete_id, 'username': username},
            timeout=10
        )
        return response.json().get('ja_respondeu', False)
    except requests.exceptions.Timeout:
        st.error("Erro: Tempo limite excedido ao verificar resposta anterior.")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao verificar resposta anterior: {str(e)}")
        return False


def handle_form_submission(
        enquete: Dict,
        username: str,
        resposta: str,
        explicacao: Optional[str] = None
) -> bool:
    """Processa o envio da resposta da enquete."""
    try:
        # Verifica se a enquete ainda está ativa
        data_fim = datetime.fromisoformat(enquete['data_fim'])
        if datetime.now() > data_fim:
            st.error("Esta enquete já expirou.")
            return False

        # Verifica se o usuário já respondeu
        if verificar_resposta_anterior(enquete['id'], username):
            st.error("Você já respondeu esta enquete anteriormente.")
            return False

        data_resposta = {
            'enquete_id': enquete['id'],
            'username': username,
            'resposta': resposta,
            'explicacao': explicacao or ""
        }

        response = requests.post(
            URL_DJANGO_RESPOSTA,
            json=data_resposta,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code in [200, 201]:
            st.success("Sua resposta foi registrada com sucesso!")
            return True
        else:
            error_msg = response.json().get('error', 'Erro desconhecido')
            st.error(f"Erro ao enviar resposta: {error_msg}")
            return False

    except requests.exceptions.Timeout:
        st.error("Erro: Tempo limite excedido ao enviar resposta.")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao enviar resposta: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        return False


def resposta_enquete():
    """Gerencia as respostas de enquetes para usuários autenticados."""
    st.title("Responder Enquetes")

    # Verifica autenticação
    if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
        st.error("Você precisa estar autenticado para responder enquetes.")
        return

    # Obtém informações do usuário da sessão
    username = st.session_state.get('username')
    role = st.session_state.get('role')

    if not username or not role:
        st.error("Informações do usuário não encontradas.")
        return

    # Obtém enquetes disponíveis da sessão (já filtradas por role no app.py)
    enquetes = st.session_state.get('enquetes_disponiveis', [])

    if not enquetes:
        st.info("Não há enquetes disponíveis para você no momento.")
        return

    # Exibe enquetes disponíveis
    st.subheader("Enquetes Disponíveis")

    df_enquetes = pd.DataFrame([{
        'ID': e['id'],
        'Título': e['titulo'],
        'Descrição': e['descricao'],
        'Início': datetime.fromisoformat(e['data_inicio']).strftime('%d/%m/%Y %H:%M'),
        'Fim': datetime.fromisoformat(e['data_fim']).strftime('%d/%m/%Y %H:%M'),
        'Direcionado a': ', '.join(e['direcionado_a'])
    } for e in enquetes])

    st.dataframe(
        df_enquetes[['Título', 'Descrição', 'Início', 'Fim', 'Direcionado a']],
        hide_index=True
    )

    # Formulário de resposta
    with st.form(key='resposta_form'):
        st.subheader("Responder Enquete")

        # Seleção da enquete
        enquete_selecionada = st.selectbox(
            "Selecione a enquete",
            options=enquetes,
            format_func=lambda x: x['titulo']
        )

        if enquete_selecionada:
            st.write("**Pergunta:**", enquete_selecionada['descricao'])

            # Opções de resposta
            opcoes = [
                enquete_selecionada.get(f'opcao{i}')
                for i in range(1, 5)
                if enquete_selecionada.get(f'opcao{i}')
            ]

            if opcoes:
                resposta = st.radio("Escolha sua resposta:", options=opcoes)
                explicacao = st.text_area("Explicação (opcional)", max_chars=500)

                submit = st.form_submit_button("Enviar Resposta")

                if submit:
                    if verificar_resposta_anterior(enquete_selecionada['id'], username):
                        st.error("Você já respondeu esta enquete.")
                    else:
                        success = handle_form_submission(
                            enquete_selecionada,
                            username,
                            resposta,
                            explicacao
                        )
                        if success:
                            st.rerun()
            else:
                st.error("Esta enquete não possui opções de resposta válidas.")
