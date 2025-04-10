import os
import streamlit as st
import requests
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from PIL import Image
from sqlalchemy.exc import IntegrityError


from decouple import config

WEBHOOK_CADASTRO = config('WEBHOOK_CADASTRO')


# Criando conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Definição da tabela oraculo_teste
class OraculoTeste(Base):
    __tablename__ = 'oraculo_teste'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    usuario = Column(String, nullable=False)
    cargo_id = Column(String, nullable=False)
    whatsapp = Column(String, nullable=False)
    password = Column(String, nullable=False)


# Função para cadastrar um novo membro no oraculo_teste
def cadastrar_dados_teste(email, usuario, cargo_id, whatsapp, password):

        session = Session()
        try:
            # Check if the email already exists
            existing_user = session.query(OraculoTeste).filter_by(email=email).first()

            if existing_user:
                st.error("❌ Este e-mail já está cadastrado!")
                return

            novo_usuario = OraculoTeste(
                email=email,
                usuario=usuario,
                cargo_id=cargo_id,
                whatsapp=whatsapp,
                password=password
            )
            session.add(novo_usuario)
            session.commit()
            st.success("✅ Usuário cadastrado com sucesso!")

        except IntegrityError as e:
            session.rollback()  # Rollback the session in case of error
            st.error("❌ Ocorreu um erro ao cadastrar o usuário. E-mail já existe.")
            print(f"IntegrityError: {e.orig}")  # Optional: Log the error for debugging
        except Exception as e:
            session.rollback()
            st.error(f"❌ Ocorreu um erro inesperado: {str(e)}")
        finally:
            session.close()


# Função para manipular o envio do formulário
def handle_form_submission(name, cpf_cnpj, email, whatsapp, endereco, cep, bairro, cidade, cargo_id, username, password, uploaded_file):
    """Salva os dados do usuário diretamente no banco de dados"""
    try:
        session = Session()

        # Verifica se o usuário já existe
        user_exist_query = text("SELECT COUNT(*) FROM oraculo_teste WHERE usuario = :username OR email = :email")
        user_exist = session.execute(user_exist_query, {"username": username, "email": email}).scalar()

        if user_exist > 0:
            st.error("❌ Usuário ou e-mail já cadastrado!")
            session.close()
            return

        # Hash da senha antes de salvar (implementar hashing)
        password_hash = password  # Substitua por hashing se necessário

        # Inserir usuário no banco
        insert_query = text("""
            INSERT INTO oraculo_teste (email, usuario, cargo_id, whatsapp, senha)
            VALUES (:email, :usuario, :cargo_id, :whatsapp, :senha)
        """)

        session.execute(insert_query, {
            "email": email,
            "usuario": username,
            "cargo_id": cargo_id,
            "whatsapp": whatsapp,
            "senha": password_hash
        })

        session.commit()
        session.close()

        st.success("✅ Usuário cadastrado com sucesso!")

        # Envio de dados para o MAKE
        data_make = {
            'name': name,
            'email': email,
            'cpf_cnpj': cpf_cnpj,
            'whatsapp': whatsapp,
            'endereco': endereco,
            'cep': cep,
            'bairro': bairro,
            'cidade': cidade,
            'cargo_id': cargo_id,
            'username': username,
            'password': password,
        }

        # Envio da requisição
        try:
            response = requests.post(cadastro_webhook, json=data_make)

            # Verifica a resposta do Webhook
            if response.status_code == 200:
                st.success("CADASTRO FEITO COM SUCESSO! 🎉", icon="🚀")
                st.balloons()
            else:
                st.error(f"Erro ao cadastrar: {response.text}")

        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar usuário: {str(e)}")

    except Exception as e:
        st.error(f"Ocorreu um erro ao tentar enviar os dados: {str(e)}")


def save_profile_image(uploaded_file, username):
    """Salva a imagem do usuário no diretório correto"""
    try:
        directory = "./media/src/img/membro"
        if not os.path.exists(directory):
            os.makedirs(directory)

        image = Image.open(uploaded_file)
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        image_path = os.path.join(directory, f"{username}.jpg")
        image.save(image_path, format="JPEG")
        return image_path

    except Exception as e:
        st.error(f"Erro ao salvar a imagem: {str(e)}")
        return None


@st.dialog("Cadastro")
def cadastrar_membro():
    """Interface de cadastro de novo membro"""
    if 'username' not in st.session_state or st.session_state.get('cargo') != 'admin':
        st.error("Acesso negado. Você precisa ser um usuário admin para acessar esta página.")
        st.stop()

    st.title("CADASTRAR NOVO MEMBRO")
    with st.header("Sistema de cadastro"):
        with st.form(key='form_cliente'):
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                name = st.text_input("Nome:")
                cpf_cnpj = st.text_input("CPF/CNPJ")

            with col2:
                email = st.text_input("E-mail")
                whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111')

            with col3:
                endereco = st.text_input("Endereço")
                bairro = st.text_input("Bairro")
                password = st.text_input("Digite uma senha:", type="password")
                uploaded_file = st.file_uploader("Escolha uma imagem de perfil", type=["jpg", "jpeg", "png"])

            with col4:
                cep = st.text_input("CEP")
                cidade = st.text_input("Cidade:")
                cargo = st.selectbox("Quem você vai cadastrar:",
                                     options=['admin', 'Pastor', 'Lider', 'Colaborador', 'Membro'])
                username = st.text_input("Usuário:")

            submit_button = st.form_submit_button("CRIAR MEMBRO!")

            if submit_button:
                handle_form_submission(name, cpf_cnpj, email, whatsapp, endereco, cep, bairro, cidade, cargo, username,
                                       password, uploaded_file)


def obter_cargos():
    with engine.connect() as connection:
        query = text("SELECT id, name FROM oraculo_cargo")  # Busca ID e nome
        result = connection.execute(query).fetchall()
        return {cargo[1]: cargo[0] for cargo in result}  # Retorna {nome: id}


@st.dialog("Cadastro-teste")
def cadastrar_teste():

    st.title("✝️ FAÇA TESTE NO ORÁCULO BÍBLIA 📖")

    # Obtém o ID do cargo 'TESTAR'
    cargos = obter_cargos()
    cargo_id = cargos.get('TESTAR')  # Supondo que 'TESTAR' sempre exista

    with st.form(key='form_cliente', clear_on_submit=True, border=True):

        email = st.text_input("E-mail")
        username = st.text_input("Usuário:")
        whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111')
        password = st.text_input("Digite uma senha:", type="password")
        uploaded_file = st.file_uploader("Escolha uma imagem de perfil", type=["jpg", "jpeg", "png"])

        submit_button = st.form_submit_button("FAZER TESTE!")

        if submit_button:
            # Cadastrar o usuário no banco de dados, passando o ID do cargo 'TESTAR'
            cadastrar_dados_teste(email, username, cargo_id, whatsapp, password)

            # Enviar dados para o Webhook (opcional)
            novo_teste = {
                "Email": email,
                "Usuário": username,
                "Cargo": 'TESTAR',  # Opcionalmente, você pode ainda enviar o nome do cargo
                "WhatsApp": whatsapp,
                "Senha": password,
                "Imagem": uploaded_file.name if uploaded_file else ""
            }
            response = requests.post(WEBHOOK_TESTE, json=novo_teste)

            if response.status_code == 200:
                st.success("🎉 Dados enviados para o webhook!")
            else:
                st.error("⚠️ Ocorreu um erro ao enviar dados para o webhook.")