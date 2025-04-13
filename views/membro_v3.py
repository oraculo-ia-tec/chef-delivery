import streamlit as st
import os
import pandas as pd
import plotly.express as px
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
import requests
from decouple import config
from pydantic import BaseModel
import hashlib

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


WEBHOOK_CADASTRO = config("WEBHOOK_CADASTRO")


# Criando conexão com o banco de dados
DATABASE_URL = config("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


# Diretório de imagens
IMAGE_DIR = "./src/img/membros"
EXCEL_FILE = "membros.xlsx"

# Criar diretório se não existir
os.makedirs(IMAGE_DIR, exist_ok=True)


# Criar arquivo Excel se não existir
if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=["ID", "Nome", "CPF/CNPJ", "WhatsApp", "Email", "Endereço", "CEP", "Bairro", "Cidade", "Cargo", "Imagem"]).to_excel(
        EXCEL_FILE, index=False, sheet_name="Membros", engine="openpyxl"
    )


# Função para salvar dados no Excel
def salvar_dados_em_excel():
    with engine.connect() as connection:
        df = pd.read_sql("SELECT * FROM oraculo_user", connection)
    df.to_excel(EXCEL_FILE, index=False, sheet_name="Membros", engine="openpyxl")


class UserData(BaseModel):
    name: str
    cpf_cnpj: str
    email: str
    whatsapp: str
    endereco: str
    cep: str
    bairro: str
    cidade: str
    cargo: str
    username: str
    password: str


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
if 'cargo' not in st.session_state:
    st.session_state.cargo = ""
if 'password' not in st.session_state:
    st.session_state.password = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'cpf_cnpj' not in st.session_state:
    st.session_state.cpf_cnpj = ""
if "image" not in st.session_state:
    st.session_state.image = None


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


def obter_cargos():
    with engine.connect() as connection:
        query = text("SELECT nome FROM oraculo_cargo")
        result = connection.execute(query)
        cargos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return cargos


def showMembro():
    # 🔹 Interface do Streamlit
    st.title("📌 Gerenciamento de Membros")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastrar", "📋 Listar", "✏️ Editar/Excluir", "📈 Estatísticas"])

    # 📝 **Aba de Cadastro de Membros**
    with tab1:
        st.header("📌 Cadastro de Membros")
        cargos = obter_cargos()

        with st.form("form_cadastro_membros", clear_on_submit=True, border=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("📝 Nome Completo")
                cpf_cnpj = st.text_input("📄 CPF ou CNPJ")
                whatsapp = st.text_input("📞 WhatsApp")
                email = st.text_input("📧 Email")
                cargo = st.selectbox("📌 Cargo", cargos)
                username = st.text_input("📧 Usuário")

            with col2:
                endereco = st.text_area("🏠 Endereço")
                cep = st.text_input("📬 CEP", max_chars=10)
                bairro = st.text_input("🏘️ Bairro")
                cidade = st.text_input("🏙️ Cidade")
                password = st.text_input("🔒 Senha", type="password")
                imagem = st.file_uploader("📸 Foto do Membro", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("✅ Cadastrar Membro")

            if submitted:
                if not all([nome, cpf_cnpj, whatsapp, email, endereco, cep, bairro, cidade, cargo, username, password]):
                    st.error("❌ Todos os campos devem ser preenchidos!")
                else:
                    session = Session()

                    # 🔹 Verificação de Unicidade do Nome de Usuário
                    user_exist_query = text("SELECT COUNT(*) FROM oraculo_user WHERE username = :username")
                    user_exist = session.execute(user_exist_query, {"username": username}).scalar()

                    if user_exist > 0:
                        st.error("❌ Nome de usuário já cadastrado! Escolha outro.")
                        session.close()
                    else:
                        try:
                            # 🔹 Gerar Hash Seguro da Senha (pode ser substituído por bcrypt)
                            password_hash = hashlib.sha256(password.encode()).hexdigest()

                            # 🔹 Salvar Imagem
                            image_path = None
                            if imagem:
                                image_path = save_profile_image(imagem, username)

                            # 🔹 Inserir no Banco de Dados
                            session.execute(text("""
                                INSERT INTO oraculo_user (name, cpf_cnpj, email, whatsapp, endereco, cep, bairro, cidade, cargo, username, password, image)
                                VALUES (:name, :cpf_cnpj, :email, :whatsapp, :endereco, :cep, :bairro, :cidade, :cargo, :username, :password, :image)
                            """), {
                                "name": nome, "cpf_cnpj": cpf_cnpj, "email": email, "whatsapp": whatsapp,
                                "endereco": endereco, "cep": cep, "bairro": bairro, "cidade": cidade, "cargo": cargo,
                                "username": username, "password": password_hash, "image": image_path
                            })

                            session.commit()
                            session.close()
                            st.success("🎉 Membro cadastrado com sucesso!")

                            # 🔹 Enviar dados para o Make via Webhook
                            data_make = {
                                "name": nome,
                                "cpf_cnpj": cpf_cnpj,
                                "email": email,
                                "whatsapp": whatsapp,
                                "endereco": endereco,
                                "cep": cep,
                                "bairro": bairro,
                                "cidade": cidade,
                                "cargo": cargo,
                                "username": username,
                                "password": password_hash
                            }

                            response = requests.post(WEBHOOK_CADASTRO, json=data_make)

                            if response.status_code == 200:
                                st.success("🎉 Dados enviados para o webhook com sucesso!")
                            else:
                                st.error(f"⚠️ Erro ao enviar dados para o webhook. Código: {response.status_code}")

                        except Exception as e:
                            st.error(f"❌ Ocorreu um erro ao tentar salvar os dados: {str(e)}")

    # Listagem de Membros
    with tab2:
        st.header("📋 Lista de Membros")
        with engine.connect() as connection:
                df = pd.read_sql("SELECT * FROM oraculo_user", connection)
        if df.empty:
            st.info("⚠️ Ainda não foi cadastrado nenhum membro.")
        else:
            pesquisa = st.chat_input("🔍 Pesquisar por nome ou CPF/CNPJ (digite os 3 primeiros caracteres)")
            if pesquisa and len(pesquisa) >= 3:  # Verifica se a pesquisa tem pelo menos 3 caracteres
                # Filtrando o DataFrame para encontrar nomes ou CPF/CNPJ que começam com os caracteres digitados
                df = df[df["name"].str.lower().str.startswith(pesquisa.lower(), na=False) |
                        df["cpf_cnpj"].str.startswith(pesquisa, na=False)]
            st.dataframe(df)

    # Edição e Exclusão de Membros
    with tab3:
        st.header("✏️ Editar ou Excluir Membro")
        with engine.connect() as connection:
            df = pd.read_sql("SELECT * FROM oraculo_user", connection)

        if df.empty:
            st.info("⚠️ Ainda não foi cadastrado nenhum membro.")
        else:
            membro_name = st.selectbox("Selecione o membro", df["name"])
            membro = df[df["name"] == membro_name].iloc[0]

            # Exibir campos de entrada para edição
            nome = st.text_input("Nome Completo", membro["name"])
            cpf_cnpj = st.text_input("CPF ou CNPJ", membro["cpf_cnpj"])
            whatsapp = st.text_input("WhatsApp", membro["whatsapp"])
            email = st.text_input("Email", membro["email"])
            endereco = st.text_area("Endereço", membro["endereco"])
            cep = st.text_input("CEP", membro["cep"])
            bairro = st.text_input("Bairro", membro["bairro"])
            cidade = st.text_input("Cidade", membro["cidade"])
            cargo = st.text_input("Cargo", membro["cargo"])  # Campo de cargo adicionado

            if st.button("💾 Salvar Alterações"):
                session = Session()
                session.execute(text("""
                    UPDATE oraculo_user SET 
                        name = :name, 
                        cpf_cnpj = :cpf_cnpj, 
                        whatsapp = :whatsapp, 
                        email = :email, 
                        endereco = :endereco,
                        cep = :cep, 
                        bairro = :bairro, 
                        cidade = :cidade, 
                        cargo = :cargo 
                    WHERE id = :id
                """), {
                    "name": nome,
                    "cpf_cnpj": cpf_cnpj,
                    "whatsapp": whatsapp,
                    "email": email,
                    "endereco": endereco,
                    "cep": cep,
                    "bairro": bairro,
                    "cidade": cidade,
                    "cargo": cargo,
                    "id": membro["id"]  # Usando o ID do membro selecionado
                })
                session.commit()
                session.close()
                salvar_dados_em_excel()
                st.success("✅ Membro atualizado com sucesso!")

            if st.button("❌ Excluir Membro"):
                session = Session()
                session.execute(text("DELETE FROM oraculo_user WHERE id = :id"), {"id": membro["id"]})
                session.commit()
                session.close()
                salvar_dados_em_excel()
                st.success("❌ Membro removido com sucesso!")

    # Estatísticas de Membros
    with tab4:
        st.header("📈 Estatísticas de Membros")

        with engine.connect() as connection:
            df = pd.read_sql("SELECT *, DATE(created_at) as data_cadastro FROM oraculo_user", connection)

        if df.empty:
            st.info("⚠️ Ainda não foi cadastrado nenhum membro.")
        else:
            total_membros = len(df)
            total_cargos = df["cargo"].nunique()

            # Filtrando novos membros cadastrados nas últimas 24 horas
            df["data_cadastro"] = pd.to_datetime(df["data_cadastro"])
            novos_membros = df[df["data_cadastro"] >= (pd.Timestamp.now() - pd.Timedelta(days=1))]
            total_novos_membros = len(novos_membros)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total de Membros", total_membros)
            with col2:
                st.metric("📌 Total de Cargos", total_cargos)
            with col3:
                st.metric("🆕 Novos Membros(24hs)", total_novos_membros)

            # Correção do gráfico de distribuição de cargos
            cargo_counts = df["cargo"].value_counts().reset_index()
            cargo_counts.columns = ["Cargo", "Quantidade"]

            fig = px.bar(
                cargo_counts,
                x="Cargo",
                y="Quantidade",
                title="Distribuição de Membros por Cargo",
                text_auto=True,
                color="Cargo"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Aplicar estilo aos cards 📌
    style_metric_cards(
        background_color="#008000",  # verde
        border_left_color="#FFFFFF",
        border_color="#000000",
        box_shadow="#FFFFFF"
    )

if __name__ == "__main__":
    st.set_page_config(page_title="Membros Recomeçar", page_icon="👥", layout="wide")
    showMembro()