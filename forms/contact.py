import streamlit as st
from datetime import datetime
import os
from PIL import Image
import requests
from decouple import config
import re


if "dialog_open" not in st.session_state:
    st.session_state.dialog_open = False

def save_profile_image(uploaded_file, email):
    if uploaded_file is None:
        return None

    directory = "src/img/cliente"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_extension = os.path.splitext(uploaded_file.name)[1]
    file_path = os.path.join(directory, f"{email}{file_extension}")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def is_valid_email(email):
    # Basic regex pattern for email validation
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None


@st.dialog("Cadastro")
def cadastrar_cliente():
    st.title("Sistema Oráculos IA")

    # Usando st.expander para criar um formulário expansível
    with st.expander("CLIQUE AQUI PARA CADASTRAR"):
        # Seção para criar um novo cliente
        with st.header("Criar Novo Cliente"):
            # Inicializa os campos no session_state se não existirem
            if 'name' not in st.session_state:
                st.session_state.name = ""
            if 'documento' not in st.session_state:
                st.session_state.documento = ""
            if 'email' not in st.session_state:
                st.session_state.email = ""
            if 'whatsapp' not in st.session_state:
                st.session_state.whatsapp = ""
            if 'endereco' not in st.session_state:
                st.session_state.endereco = ""
            if 'cep' not in st.session_state:
                st.session_state.cep = ""
            if 'bairro' not in st.session_state:
                st.session_state.bairro = ""
            if 'cidade' not in st.session_state:
                st.session_state.cidade = ""
            if 'role' not in st.session_state:
                st.session_state.role = ""
            if 'password' not in st.session_state:
                st.session_state.password = ""
            if 'username' not in st.session_state:
                st.session_state.username = ""

            # Formulário para cadastro de cliente
            with st.form(key='form_cliente'):
                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                with col1:
                    name = st.text_input("Nome:", value=st.session_state.name)
                    documento = st.text_input("CPF/CNPJ", value=st.session_state.documento)
                with col2:
                    email = st.text_input("E-mail", value=st.session_state.email)
                    whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)
                with col3:
                    endereco = st.text_input("Endereço", value=st.session_state.endereco)
                    bairro = st.text_input("Bairro", value=st.session_state.bairro)
                    password = st.text_input("Digite uma senha:", type="password", value=st.session_state.password)
                with col4:
                    cep = st.text_input("CEP", value=st.session_state.cep)
                    cidade = st.text_input("Cidade:", value=st.session_state.cidade)
                    role = st.selectbox(
                        "Tipo de Usuário",
                        options=["cliente", "parceiro", "admin"],
                        index=0 if not st.session_state.role else ["cliente", "parceiro", "admin"].index(st.session_state.role))
                    username = st.text_input("Usuário:", value=st.session_state.username)

                submit_button = st.form_submit_button("CRIAR CLIENTE!")

                if submit_button:
                    # Atualiza o session_state com os valores do formulário
                    st.session_state.name = name
                    st.session_state.documento = documento
                    st.session_state.email = email
                    st.session_state.whatsapp = whatsapp
                    st.session_state.endereco = endereco
                    st.session_state.cep = cep
                    st.session_state.bairro = bairro
                    st.session_state.cidade = cidade
                    st.session_state.role = role
                    st.session_state.username = username
                    st.session_state.password = password

                    # Validação dos dados do cliente
                    try:
                        for field in ['name', 'email', 'documento', 'whatsapp', 'endereco', 'cep', 'bairro', 'cidade', 'role', 'username', 'password']:
                            if not st.session_state[field]:
                                raise ValueError(f"O campo {field} é obrigatório.")

                        # Preparar os dados para envio ao Make
                        data_make = {
                            "name": st.session_state.name,
                            "cpf_cnpj": st.session_state.documento,
                            "email": st.session_state.email,
                            "whatsapp": st.session_state.whatsapp,
                            "endereco": st.session_state.endereco,
                            "cep": st.session_state.cep,
                            "bairro": st.session_state.bairro,
                            "cidade": st.session_state.cidade,
                            "role": st.session_state.role,
                            "username": st.session_state.username,
                            "password": st.session_state.password,
                        }

                        # Enviar os dados para o Make via Webhook
                        WEBHOOK_CADASTRO = config("WEBHOOK_URL")
                        response = requests.post(WEBHOOK_CADASTRO, json=data_make)

                        # Verificar a resposta do Webhook
                        if response.status_code == 200:
                            st.success("CADASTRO FEITO COM SUCESSO! 🎉", icon="🚀")
                            st.balloons()
                        else:
                            st.error("Desculpe-me, parece que houve um problema no envio da sua mensagem", icon="😨")
                    except ValueError as ve:
                        st.error(str(ve))  # Exibe um erro de validação ao usuário
                    except requests.exceptions.RequestException as e:
                        st.error(f"Ocorreu um erro ao tentar enviar a mensagem: {e}", icon="⚠️")


@st.dialog("Agendamento")
def agendar_reuniao():
    st.title("Agendamento de Reunião")

    # Usando st.expander para criar um formulário expansível
    with st.expander("Clique aqui para Agendar sua Reunião"):
        with st.form("cadastro_reuniao"):
            # Campos do formulário
            name = st.text_input("Nome:")
            whatsapp = st.text_input("WhatsApp:")
            email = st.text_input("E-mail:")
            username = st.text_input("Usuário:", placeholder="CRIE UM USUÁRIO PARA ACESSAR")
            password = st.text_input("Senha:", placeholder="CRIE SUA SENHA PARA ACESSAR", type="password")
            message = st.text_area("Mensagem:")

            # Selecionar o dia da semana
            dias_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
            dia_selecionado = st.selectbox("Escolha o Dia da Reunião:", dias_da_semana)

            # Selecionar o horário com base no dia selecionado
            horarios = {
                "Segunda": ["09:00", "10:00", "11:00", "14:00", "15:00"],
                "Terça": ["09:00", "10:00", "11:00", "14:00", "15:00"],
                "Quarta": ["09:00", "10:00", "11:00", "14:00", "15:00"],
                "Quinta": ["09:00", "10:00", "11:00", "14:00", "15:00"],
                "Sexta": ["09:00", "10:00", "11:00", "14:00", "15:00"],
            }
            horario_selecionado = st.selectbox("Escolha o Horário:", horarios[dia_selecionado])

            # Botão de envio
            submit_button = st.form_submit_button("ENVIAR")

            # Lógica de envio
            if submit_button:
                if not WEBHOOK_URL:
                    st.error("O Webhook deverá ser configurado", icon="📧")
                    st.stop()

                # Preparar os dados para envio
                data = {
                    "Nome": name,
                    "WhatsApp": whatsapp,
                    "Email": email,
                    "Usuário": username,
                    "Senha": password,
                    "Mensagem": message,
                    "Dia": dia_selecionado,
                    "Horário": horario_selecionado,
                }

                # Enviar a requisição ao Webhook
                try:
                    response = requests.post(WEBHOOK_AGENDA, json=data)

                    # Verificar a resposta do Webhook
                    if response.status_code == 200:
                        st.success(
                            "A sua mensagem foi enviada, o Alan entrará em contato! 🎉",
                            icon="🚀",
                        )
                        st.balloons()
                    else:
                        st.error(
                            "Desculpe-me, parece que houve um problema no envio da sua mensagem",
                            icon="😨",
                        )
                except requests.exceptions.RequestException as e:
                    st.error(
                        f"Ocorreu um erro ao tentar enviar a mensagem: {e}", icon="⚠️"
                    )


@st.dialog("Oráculo Coach")
def cadastro_teste():
    st.title("Cadastro de Teste")

    # Inicializa os campos no session_state se não existirem
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = ""
    if 'endereco' not in st.session_state:
        st.session_state.endereco = ""
    if 'cep' not in st.session_state:
        st.session_state.cep = ""
    if 'bairro' not in st.session_state:
        st.session_state.bairro = ""
    if 'cidade' not in st.session_state:
        st.session_state.cidade = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'cpf_cnpj' not in st.session_state:
        st.session_state.cpf_cnpj = ""

    # Formulário para cadastro de teste
    with st.form(key='form_teste'):
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        with col1:
            name = st.text_input("Nome:", value=st.session_state.name)
            cpf_cnpj = st.text_input("CPF/CNPJ", value=st.session_state.cpf_cnpj)
        with col2:
            email = st.text_input("E-mail", value=st.session_state.email)
            whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)
        with col3:
            endereco = st.text_input("Endereço", value=st.session_state.endereco)
            bairro = st.text_input("Bairro", value=st.session_state.bairro)
            password = st.text_input("Digite uma senha:", type="password", value=st.session_state.password)
        with col4:
            cep = st.text_input("CEP", value=st.session_state.cep)
            cidade = st.text_input("Cidade:", value=st.session_state.cidade)
            username = st.text_input("Usuário:", value=st.session_state.username)

        submit_button = st.form_submit_button("ENVIAR!")

        if submit_button:
            # Atualiza o session_state com os valores do formulário
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.whatsapp = whatsapp
            st.session_state.endereco = endereco
            st.session_state.cep = cep
            st.session_state.bairro = bairro
            st.session_state.cidade = cidade
            st.session_state.password = password
            st.session_state.username = username
            st.session_state.cpf_cnpj = cpf_cnpj

            # Validação dos dados do cliente
            try:
                for field in ['name', 'email', 'whatsapp', 'endereco', 'cep', 'bairro', 'cidade', 'password', 'username', 'cpf_cnpj']:
                    if not st.session_state[field]:
                        raise ValueError(f"O campo {field} é obrigatório.")

                # Preparar os dados para envio ao Make
                data_make = {
                    "name": st.session_state.name,
                    "cpf_cnpj": st.session_state.cpf_cnpj,
                    "email": st.session_state.email,
                    "whatsapp": st.session_state.whatsapp,
                    "endereco": st.session_state.endereco,
                    "cep": st.session_state.cep,
                    "bairro": st.session_state.bairro,
                    "cidade": st.session_state.cidade,
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                }

                # Enviar os dados para o Make via Webhook
                WEBHOOK_TESTE = config("WEBHOOK_TESTE")
                response = requests.post(WEBHOOK_TESTE, json=data_make)

                # Verificar a resposta do Webhook
                if response.status_code == 200:
                    st.success("Cadastro feito com sucesso! 🎉", icon="🚀")
                    st.balloons()
                else:
                    st.error("Desculpe-me, parece que houve um problema no envio da sua mensagem", icon="😨")
            except ValueError as ve:
                st.error(str(ve))  # Exibe um erro de validação ao usuário
            except requests.exceptions.RequestException as e:
                st.error(f"Ocorreu um erro ao tentar enviar a mensagem: {e}", icon="⚠️")
