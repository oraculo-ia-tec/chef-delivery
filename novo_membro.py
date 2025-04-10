import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, Date, DateTime, Boolean, JSON, text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, date
from streamlit_extras.metric_cards import style_metric_cards
from key_config import DATABASE_URL  # Certifique-se de que este arquivo existe e contém a URL do banco de dados
from util import formatar_data_hora


# Criando conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Definição da classe NovoMembro para representar a tabela oraculo_novomembro
class NovoMembro(Base):
    __tablename__ = "oraculo_novomembro"
    id = Column(Integer, primary_key=True, autoincrement=True)
    culto_id = Column(Integer, nullable=False)
    decisao = Column(Enum("ACEITEI JESUS", "DECIDI VOLTAR"), nullable=False)
    name = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(255), nullable=False)
    whatsapp = Column(String(20), nullable=False)
    cargo = Column(Enum("admin", "Pastor", "Lider", "Colaborador", "Membro"), nullable=False)
    endereco = Column(String(255))
    numero_residencia = Column(String(10))
    cep = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(50))
    estado_civil = Column(Enum("Solteiro", "Casado", "Divorciado", "Viúvo"))
    nome_conjuge = Column(String(255))
    data_nascimento_conjuge = Column(Date)
    data_casamento = Column(Date)
    nome_falecida = Column(String(255))
    data_nascimento_falecida = Column(Date)
    data_falecimento = Column(Date)
    tem_filhos = Column(Boolean, default=False)
    numero_filhos = Column(Integer, default=0)
    filhos = Column(JSON)  # Armazena os dados dos filhos como JSON
    era_igreja_anterior = Column(Boolean, default=False)
    nome_igreja_anterior = Column(String(255))
    cargo_igreja_anterior = Column(String(255))
    pastor_presidente = Column(String(255))
    deseja_explicar_saida = Column(Boolean, default=False)
    motivo_saida = Column(Text)
    fazia_ministerio = Column(String(255))
    data_conversao = Column(Date)
    participa_departamento = Column(String(255))
    facebook = Column(String(255))
    instagram = Column(String(255))
    twitter = Column(String(255))
    linkedin = Column(String(255))
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    imagem_perfil = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Lista corrigida de campos do novo membro
campos_novo_membro = [
    "culto_id", "decisao", "name", "data_nascimento", "email", "whatsapp", "cargo", "endereco", "numero_residencia",
    "cep", "bairro", "cidade", "estado",
    "estado_civil", "nome_conjuge", "data_nascimento_conjuge", "data_casamento", "nome_falecida",
    "data_nascimento_falecida", "data_falecimento", "tem_filhos", "numero_filhos", "filhos",
    "era_igreja_anterior", "nome_igreja_anterior", "cargo_igreja_anterior", "pastor_presidente",
    "deseja_explicar_saida", "motivo_saida", "fazia_ministerio", "data_conversao", "participa_departamento",
    "facebook", "instagram", "twitter", "linkedin", "username", "password", "imagem_perfil"
]

# Loop para inicializar os campos no session_state
for campo in campos_novo_membro:
    if campo not in st.session_state:
        if campo in ["tem_filhos", "era_igreja_anterior", "deseja_explicar_saida"]:
            st.session_state[campo] = False  # Campos booleanos
        elif campo == "filhos":
            st.session_state[campo] = []  # Campo de filhos (lista)
        elif campo == "numero_filhos":
            st.session_state[campo] = 0  # Inicializa como 0 (inteiro)
        else:
            st.session_state[campo] = ""  # Outros campos (strings)


def obter_cargos():
    with engine.connect() as connection:
        query = text("SELECT name FROM oraculo_cargo")
        result = connection.execute(query)
        cargos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return cargos


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


# Função principal para exibir o formulário de cadastro de novo membro
def show_novo_membro():
    # Inicializando o estado da sessão para cada campo
    st.session_state.decisao = st.session_state.get("decisao", "")
    st.session_state.culto_id = st.session_state.get("culto_id", 1)  # Valor padrão
    st.session_state.name = st.session_state.get("name", "")
    st.session_state.data_nascimento = st.session_state.get("data_nascimento", "")
    st.session_state.email = st.session_state.get("email", "")
    st.session_state.whatsapp = st.session_state.get("whatsapp", "")
    st.session_state.cargo = st.session_state.get("cargo", "Membro")
    st.session_state.endereco = st.session_state.get("endereco", "")
    st.session_state.numero_residencia = st.session_state.get("numero_residencia", "")
    st.session_state.complemento = st.session_state.get("complemento", "")  # Novo campo
    st.session_state.cep = st.session_state.get("cep", "")
    st.session_state.bairro = st.session_state.get("bairro", "")
    st.session_state.cidade = st.session_state.get("cidade", "")
    st.session_state.estado = st.session_state.get("estado", "")
    st.session_state.estado_civil = st.session_state.get("estado_civil", "")
    st.session_state.tem_filhos = st.session_state.get("tem_filhos", "Não")
    st.session_state.numero_filhos = st.session_state.get("numero_filhos", 0)
    st.session_state.filhos = st.session_state.get("filhos", "[]")
    st.session_state.era_igreja_anterior = st.session_state.get("era_igreja_anterior", "Não")
    st.session_state.igreja_anterior = st.session_state.get("nome_igreja_anterior", "")
    st.session_state.cargo_igreja_anterior = st.session_state.get("cargo_igreja_anterior", "")
    st.session_state.deseja_explicar_saida = st.session_state.get("deseja_explicar_saida", "Não")
    st.session_state.motivo_saida = st.session_state.get("motivo_saida", "")
    st.session_state.data_conversao = st.session_state.get("data_conversao", "")
    st.session_state.facebook = st.session_state.get("facebook", "")
    st.session_state.instagram = st.session_state.get("instagram", "")
    st.session_state.twitter = st.session_state.get("twitter", "")
    st.session_state.linkedin = st.session_state.get("linkedin", "")
    st.session_state.username = st.session_state.get("username", "")
    st.session_state.password = st.session_state.get("password", "")
    st.session_state.imagem_perfil = st.session_state.get("imagem_perfil")
    st.session_state.preferencias_contato = st.session_state.get("preferencias_contato", "WhatsApp")  # Novo campo
    st.session_state.observacoes = st.session_state.get("observacoes", "")  # Novo campo

    # Interface do Streamlit
    st.title("✝️ Gerenciamento de Novos Membros")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastrar",
                                      "📋 Listar",
                                      "✏️ Editar/Excluir",
                                      "📊 Estatísticas"])

    # Tab 1: Cadastro
    with tab1:
        st.header("➕ Cadastro de Novo Membro")
        st.markdown("Preencha os campos abaixo para cadastrar um novo membro.")

        with st.form("form_novo_membro", clear_on_submit=True, border=True):
            # Section 1: Decision and Cult Selection
            col1, col2 = st.columns(2)
            with col1:
                decisao = st.radio(
                    "Decisão Espiritual",
                    ["ACEITEI JESUS", "DECIDI VOLTAR"],
                    horizontal=True
                )
                st.session_state.decisao = decisao  # Update session state

            with col2:
                cultos = obter_nomes_cultos()
                if not cultos:
                    st.warning("⚠️ Nenhum culto cadastrado. Cadastre um culto antes de continuar.")
                    st.stop()

                culto_selecionado = st.selectbox(
                    "Em qual culto você tomou essa decisão?",
                    list(cultos.keys())
                )
                culto_id = cultos[culto_selecionado]
                st.session_state.culto_id = culto_id  # Update session state

            # Section 2: Personal Information
            with st.expander("👤 Dados Pessoais"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Nome Completo", placeholder="Digite o nome completo",
                                         value=st.session_state.get("name", ""))
                    data_nascimento = st.date_input(
                        "Data de Nascimento",
                        min_value=date(1900, 1, 1),
                        max_value=date.today(),
                        value=formatar_data_hora(st.session_state.get("data_nascimento"))
                    )
                    email = st.text_input("E-mail", placeholder="exemplo@email.com",
                                          value=st.session_state.get("email", ""))
                    whatsapp = st.text_input("WhatsApp", placeholder="(XX) XXXXX-XXXX",
                                             value=st.session_state.get("whatsapp", ""))

                with col2:
                    cargo = st.selectbox(
                        "Cargo na Igreja",
                        ["admin", "Pastor", "Líder", "Colaborador", "Membro"],
                        index=0
                    )
                    endereco = st.text_input("Endereço", placeholder="Rua/Avenida",
                                             value=st.session_state.get("endereco", ""))
                    numero_residencia = st.text_input("Número", placeholder="Número da residência",
                                                      value=st.session_state.get("numero_residencia", ""))
                    cep = st.text_input("CEP", placeholder="XXXXX-XXX", value=st.session_state.get("cep", ""))
                    bairro = st.text_input("Bairro", placeholder="Nome do bairro",
                                           value=st.session_state.get("bairro", ""))
                    cidade = st.text_input("Cidade", placeholder="Nome da cidade",
                                           value=st.session_state.get("cidade", ""))
                    estado = st.text_input("Estado", placeholder="UF", value=st.session_state.get("estado", ""))

            # Section 3: Family Information
            with st.expander("👨‍👩‍👧‍👦 Dados Familiares"):
                col1, col2 = st.columns(2)
                with col1:
                    estado_civil = st.radio("Estado Civil", ["Solteiro", "Casado", "Divorciado", "Viúvo"],
                                            horizontal=True)
                    tem_filhos = st.radio("Tem filhos?", ["Sim", "Não"], horizontal=True, key="tem_filhos")

                with col2:
                    numero_filhos = 0
                    if tem_filhos == "Sim":
                        numero_filhos = st.number_input(
                            "Quantos filhos?",
                            min_value=0,
                            max_value=20,
                            value=st.session_state.get("numero_filhos", 0),
                            step=1,
                            key="numero_filhos"
                        )

                # Collect children's data if applicable
                filhos = []
                if numero_filhos > 0:
                    for i in range(numero_filhos):
                        with st.container():
                            st.write(f"Filho {i + 1}")
                            nome_filho = st.text_input(f"Nome do Filho {i + 1}", key=f"nome_filho_{i}")
                            data_nascimento_filho = st.date_input(
                                f"Data de Nascimento do Filho {i + 1}",
                                value=date.today(),
                                min_value=date(1900, 1, 1),
                                max_value=date.today(),
                                key=f"data_nascimento_filho_{i}"
                            )
                            filhos.append({
                                "nome_filho": nome_filho,
                                "data_nascimento_filho": data_nascimento_filho.strftime('%d/%m/%Y')
                            })

            # Section 4: Spiritual Information
            with st.expander("✝️ Dados Espirituais"):
                col1, col2 = st.columns(2)
                with col1:
                    era_igreja_anterior = st.radio("Frequentava outra igreja antes?", ["Sim", "Não"], horizontal=True)

                with col2:
                    igreja_anterior = ""
                    cargo_igreja_anterior = ""
                    motivo_saida = ""
                    deseja_explicar_saida = ""

                    if era_igreja_anterior == "Sim":
                        igreja_anterior = st.text_input("Nome da Igreja Anterior",
                                                        value=st.session_state.get("nome_igreja_anterior", ""))
                        cargo_igreja_anterior = st.text_input("Cargo na Igreja Anterior",
                                                              value=st.session_state.get("cargo_igreja_anterior", ""))
                        deseja_explicar_saida = st.radio("Deseja explicar o motivo da saída?", ["Sim", "Não"],
                                                         horizontal=True)

                        if deseja_explicar_saida == "Sim":
                            motivo_saida = st.text_area("Motivo da Saída",
                                                        value=st.session_state.get("motivo_saida", ""))

            # Section 5: Social Media
            with st.expander("📱 Redes Sociais"):
                col1, col2 = st.columns(2)
                with col1:
                    facebook = st.text_input("Facebook", placeholder="Link do perfil",
                                             value=st.session_state.get("facebook", ""))
                    instagram = st.text_input("Instagram", placeholder="Link do perfil",
                                              value=st.session_state.get("instagram", ""))

                with col2:
                    twitter = st.text_input("Twitter", placeholder="Link do perfil",
                                            value=st.session_state.get("twitter", ""))
                    linkedin = st.text_input("LinkedIn", placeholder="Link do perfil",
                                             value=st.session_state.get("linkedin", ""))

            # Section 6: Access Credentials
            with st.expander("🔒 Dados de Acesso ao Oráculo Bíblia"):
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("Username", placeholder="Escolha um nome de usuário",
                                             value=st.session_state.get("username", ""))
                with col2:
                    password = st.text_input("Senha", type="password", placeholder="Escolha uma senha segura",
                                             value=st.session_state.get("password", ""))

            # Section 7: Profile Picture
            with st.expander("🖼️ Imagem de Perfil"):
                imagem_perfil = st.file_uploader("Upload da Foto", type=["jpg", "jpeg", "png"],
                                                 accept_multiple_files=False)

            # Submit Button
            submitted = st.form_submit_button("✅ Cadastrar Novo Membro")
            if submitted:
                # Validate required fields
                if not all([name.strip(), email.strip(), whatsapp.strip(), cargo.strip()]):
                    st.error("⚠️ Preencha todos os campos obrigatórios.")
                else:
                    try:
                        with Session() as session:
                            query = text("""
                                    INSERT INTO oraculo_novomembro (
                                        culto_id, decisao, name, data_nascimento, email, whatsapp, cargo, endereco, numero_residencia,
                                        cep, bairro, cidade, estado, estado_civil, tem_filhos, numero_filhos, filhos,
                                        era_igreja_anterior, nome_igreja_anterior, cargo_igreja_anterior, deseja_explicar_saida, motivo_saida,
                                        data_conversao, facebook, instagram, twitter, linkedin, username, password, imagem_perfil
                                    )
                                    VALUES (
                                        :culto_id, :decisao, :name, :data_nascimento, :email, :whatsapp, :cargo, :endereco, :numero_residencia,
                                        :cep, :bairro, :cidade, :estado, :estado_civil, :tem_filhos, :numero_filhos, :filhos,
                                        :era_igreja_anterior, :nome_igreja_anterior, :cargo_igreja_anterior, :deseja_explicar_saida, :motivo_saida,
                                        :data_conversao, :facebook, :instagram, :twitter, :linkedin, :username, :password, :imagem_perfil
                                    )
                                """)
                            session.execute(
                                query,
                                {
                                    "culto_id": st.session_state.culto_id,
                                    "decisao": decisao,
                                    "name": name,
                                    "data_nascimento": data_nascimento,
                                    "email": email,
                                    "whatsapp": whatsapp,
                                    "cargo": cargo,
                                    "endereco": endereco,
                                    "numero_residencia": numero_residencia,
                                    "cep": cep,
                                    "bairro": bairro,
                                    "cidade": cidade,
                                    "estado": estado,
                                    "estado_civil": estado_civil,
                                    "tem_filhos": tem_filhos == "Sim",
                                    "numero_filhos": int(numero_filhos),
                                    "filhos": str(filhos),
                                    "era_igreja_anterior": era_igreja_anterior == "Sim",
                                    "nome_igreja_anterior": igreja_anterior,
                                    "cargo_igreja_anterior": cargo_igreja_anterior,
                                    "deseja_explicar_saida": deseja_explicar_saida == "Sim",
                                    "motivo_saida": motivo_saida,
                                    "data_conversao": data_conversao,
                                    "facebook": facebook,
                                    "instagram": instagram,
                                    "twitter": twitter,
                                    "linkedin": linkedin,
                                    "username": username,
                                    "password": password,
                                    "imagem_perfil": imagem_perfil.name if imagem_perfil else None
                                }
                            )
                            session.commit()
                            st.success("🎉 Novo Membro cadastrado com sucesso!")
                            st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar membro: {e}")

    # Aba de Listagem de Novos Membros
    with tab2:
        st.expander("📋 Lista de Novos Membros")
        with Session() as session:
            membros = session.execute(
                text("SELECT id, name, email, whatsapp, cargo FROM oraculo_novomembro")
            ).fetchall()

        if not membros:
            st.info("⚠️ Nenhum membro cadastrado.")
        else:
            df = pd.DataFrame(membros, columns=["ID", "Nome", "Email", "WhatsApp", "Cargo"])
            st.dataframe(df)

    # Aba de Edição e Exclusão de Novos Membros
    with tab3:
        st.expander("✏️ Editar ou Excluir Membro")
        with Session() as session:
            membros = session.execute(text("SELECT id, name FROM oraculo_novomembro")).fetchall()

        if not membros:
            st.info("⚠️ Nenhum membro cadastrado.")
        else:
            membro_ids = [m[0] for m in membros]
            membro_nomes = [m[1] for m in membros]
            membro_selecionado = st.selectbox("Selecione um membro para editar/excluir", membro_ids, format_func=lambda x: membro_nomes[membro_ids.index(x)])

            novo_nome = st.text_input("Novo Nome do Membro")
            novo_email = st.text_input("Novo Email")

            if st.button("💾 Atualizar Membro"):
                with Session() as session:
                    session.execute(
                        text("UPDATE oraculo_novomembro SET name=:novo_nome, email=:novo_email WHERE id=:id"),
                        {"novo_nome": novo_nome, "novo_email": novo_email, "id": membro_selecionado}
                    )
                    session.commit()
                    st.success("✅ Membro atualizado com sucesso!")

            if st.button("❌ Excluir Membro"):
                with Session() as session:
                    session.execute(text("DELETE FROM oraculo_novomembro WHERE id=:id"), {"id": membro_selecionado})
                    session.commit()
                    st.success("❌ Membro excluído com sucesso!")

    # Aba de Estatísticas
    with tab4:
        st.expander("📊 Estatísticas de Novos Membros")
        with Session() as session:
            total_membros = session.execute(text("SELECT COUNT(*) FROM oraculo_novomembro")).scalar()
            total_aceitaram_jesus = session.execute(
                text("SELECT COUNT(*) FROM oraculo_novomembro WHERE decisao = 'ACEITEI JESUS'")
            ).scalar()
            total_voltaram = session.execute(
                text("SELECT COUNT(*) FROM oraculo_novomembro WHERE decisao = 'DECIDI VOLTAR'")
            ).scalar()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Novos Membros", total_membros)
        with col2:
            st.metric("Aceitaram Jesus", total_aceitaram_jesus)
        with col3:
            st.metric("Decidiram Voltar", total_voltaram)

        style_metric_cards(
            background_color="#008000",
            border_left_color="#FFFFFF",
            border_color="#000000",
            box_shadow="#FFFFFF"
        )

        fig = px.bar(
            x=["Aceitaram Jesus", "Decidiram Voltar"],
            y=[total_aceitaram_jesus, total_voltaram],
            title="Decisões dos Novos Membros"
        )
        st.plotly_chart(fig, use_container_width=True)