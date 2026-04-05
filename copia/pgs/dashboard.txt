import streamlit as st

# Dashboard simples para gerenciamento de usuários logados

def showDashboard():
    st.title("Dashboard - Usuários Logados")
    st.write("Aqui você pode visualizar e gerenciar os usuários atualmente logados no sistema.")

    # Simulação de usuários logados usando session_state
    if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
        st.success(f"Usuário logado: {st.session_state['username']}")
    else:
        st.warning("Nenhum usuário autenticado no momento.")

    st.info("Funcionalidades futuras: listagem de todos os usuários ativos, gerenciamento de permissões, etc.")
