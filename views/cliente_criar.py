import streamlit as st
import os
import pandas as pd
import plotly.express as px
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
import requests
from pydantic import BaseModel
import hashlib

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from decouple import config


WEBHOOK_CADASTRO = config('WEBHOOK_CADASTRO')
DATABASE_URL = config('DATABASE_URL')
# Inicializa o aplicativo FastAPI


# Criando conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


# Diretório de imagens
IMAGE_DIR = "./media/src/img/membro"
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
    decisao: str  # Adicionado para armazenar a decisão espiritual
    culto_id: int  # Adicionado para armazenar o ID do culto
    estado_civil: str  # Adicionado para armazenar o estado civil
    filhos: int = 0  # Adicionado para armazenar o número de filhos, padrão 0


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
if 'image' not in st.session_state:
    st.session_state.image = None
if 'decisao' not in st.session_state:
    st.session_state.decisao = ""
if 'culto_id' not in st.session_state:
    st.session_state.culto_id = None  # Inicializa como None pois é um ID
if 'estado_civil' not in st.session_state:
    st.session_state.estado_civil = ""
if 'filhos' not in st.session_state:
    st.session_state.filhos = 0  # Inicializa com 0 caso o usuário não tenha filhos


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
        query = text("SELECT id, name FROM oraculo_cargo")  # Busca ID e nome
        result = connection.execute(query).fetchall()
        return {cargo[1]: cargo[0] for cargo in result}  # Retorna {nome: id}


def obter_nomes_cultos():
    """Busca todos os cultos cadastrados e retorna um dicionário {nome_culto: id}."""
    try:
        with engine.connect() as connection:
            query = text("SELECT id, nome_culto FROM oraculo_culto")
            result = connection.execute(query).fetchall()
            cultos = {culto[1]: culto[0] for culto in result}  # {nome: id}
            return cultos
    except Exception as e:
        st.error(f"⚠️ Erro ao buscar cultos: {e}")
        return {}


# Mapeamento de emojis para as decisões
option_map = {
    "ACEITEI JESUS": "✝️",
    "DECIDI VOLTAR": "🔄"
}


def showMembro():
    # 🔹 Interface do Streamlit
    st.title("📌 Gerenciamento de Membros")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastrar", "📋 Listar", "✏️ Editar/Excluir", "📈 Estatísticas"])

    # 📝 **Aba de Cadastro de Membros**
    with tab1:
        st.header("📌 Cadastro de Membros")
        cargos_dict = obter_cargos()  # Retorna {nome: id}
        cargos_nomes = list(cargos_dict.keys())

        with st.form("form_cadastro_membros", clear_on_submit=True, border=True):
            # Controle segmentado para a decisão espiritual
            col1, col2 = st.columns(2)
            with col1:
                decisao = st.segmented_control(
                    "Decisão Espiritual",
                    options=list(option_map.keys()),
                    format_func=lambda option: option_map[option] + " " + option,  # Adiciona emoji antes da decisão
                    selection_mode="single",
                )

                # Atualiza o estado da sessão com a decisão escolhida
                st.session_state.decisao = decisao

                # Mensagem de parabenização condicional
                if st.session_state.decisao == "ACEITEI JESUS":
                    st.success(
                        "🎉 Parabéns pela sua escolha: **ACEITEI JESUS**! Você está começando uma nova jornada "
                        "espiritual.")
                    st.rerun()
                elif st.session_state.decisao == "DECIDI VOLTAR":
                    st.success(
                        "🎉 Parabéns pela sua escolha: **DECIDI VOLTAR**! É maravilhoso ver você de volta à "
                        "comunidade.")
                    st.rerun()

            # Obter nomes dos cultos
            cultos = obter_nomes_cultos()
            with col2:
                if cultos:
                    culto_selecionado = st.radio(
                        "Em qual ⛪culto você tomou a decisão?",
                        options=list(cultos.keys()),
                        format_func=lambda x: f"{x}",
                    )
                    culto_id = cultos[culto_selecionado]  # Atribui culto_id corretamente
                    st.session_state.culto_id = culto_id

            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("📝 Nome Completo")
                cpf_cnpj = st.text_input("📄 CPF ou CNPJ")
                whatsapp = st.text_input("📞 WhatsApp")
                email = st.text_input("📧 Email")
                estado_civil = st.selectbox("💍 Estado Civil",
                                            ["Solteiro", "Casado", "Divorciado", "Viúvo"])  # Campo para estado civil
                cargo_selecionado = st.selectbox("Cargo", cargos_nomes)
                cargo_id = cargos_dict[cargo_selecionado]
                username = st.text_input("📧 Usuário")


            with col2:
                endereco = st.text_area("🏠 Endereço")
                cep = st.text_input("📬 CEP", max_chars=10)
                bairro = st.text_input("🏘️ Bairro")
                cidade = st.text_input("🏙️ Cidade")
                filhos = st.number_input("👶 Número de Filhos", min_value=0, step=1)  # Campo para número de filhos
                password = st.text_input("🔒 Senha", type="password")
                imagem = st.file_uploader("📸 Foto do Membro", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("✅ Cadastrar Membro")

            if submitted:
                if not all([nome, cpf_cnpj, whatsapp, email, endereco, cep, bairro, cidade, cargo_selecionado, username, password,
                            decisao, culto_id, estado_civil]):
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
                                   INSERT INTO oraculo_user (name, cpf_cnpj, email, whatsapp, endereco, cep, bairro, cidade, cargo_id, username, password, image, decisao, culto_id, estado_civil, filhos)
                                   VALUES (:name, :cpf_cnpj, :email, :whatsapp, :endereco, :cep, :bairro, :cidade, :cargo_id, :username, :password, :image, :decisao, :culto_id, :estado_civil, :filhos)
                               """), {
                                "name": nome, "cpf_cnpj": cpf_cnpj, "email": email, "whatsapp": whatsapp,
                                "endereco": endereco, "cep": cep, "bairro": bairro, "cidade": cidade, "cargo_id": cargo_id,
                                "username": username, "password": password_hash, "image": image_path,
                                "decisao": decisao, "culto_id": culto_id, "estado_civil": estado_civil, "filhos": filhos
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
                                "cargo": cargo_selecionado,
                                "username": username,
                                "password": password_hash,
                                "decisao": decisao,
                                "culto_id": culto_selecionado,
                                "estado_civil": estado_civil,
                                "filhos": filhos
                            }

                            response = requests.post(WEBHOOK_CADASTRO, json=data_make)

                            if response.status_code == 200:
                                st.success("🎉 Dados enviados para o webhook com sucesso!")
                                st.balloons()
                                st.rerun()
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
            cargo = st.text_input("Cargo", membro["cargo_id"])  # Campo de cargo adicionado

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
                        cargo_id = :cargo 
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
                    "cargo_id": cargo,
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
            total_cargos = df["cargo_id"].nunique()

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
            cargo_counts = df["cargo_id"].value_counts().reset_index()
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
    st.set_page_config(page_title="Cadastro de Membros", page_icon="👥", layout="wide")
    showMembro()  # Chama a função que será responsável pela lógica da página de criação de membros
