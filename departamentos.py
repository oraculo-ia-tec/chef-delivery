import streamlit as st
import os
import pandas as pd
import plotly.express as px
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
from datetime import datetime
import re
import replicate


from key_config import DATABASE_URL, WEBHOOK_CADASTRO
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


# Criando conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
# Configuração básica do SQLAlchemy
Base = declarative_base()


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


class GestaoDepartamentos(Base):
    """
    Classe que representa a tabela 'gestao_departamentos' no banco de dados.
    Esta tabela armazena informações sobre departamentos gerenciados pela igreja.
    """
    __tablename__ = "gestao_departamentos"

    # Definição dos campos da tabela
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único do departamento")
    created_dt = Column(DateTime, default=datetime.now, nullable=False, comment="Data de criação do registro")
    updated_dt = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="Data de atualização do registro")
    active_dt = Column(DateTime, nullable=True, comment="Data de ativação do departamento")
    departamento = Column(String(100), nullable=False, comment="Nome do departamento")
    descricao = Column(Text, nullable=True, comment="Descrição detalhada do departamento")
    img = Column(String(100), nullable=True, comment="Caminho ou URL da imagem do departamento")
    name_lider = Column(String(255), nullable=True, comment="Nome do líder responsável pelo departamento")


def obter_nomes_lideres():
    """Retorna lista de pastores (id, nome) do banco de dados"""
    with get_db_session() as session:
        query = text("""
                SELECT u.id, u.name 
                FROM oraculo_user u
                JOIN oraculo_cargo c ON u.cargo_id = c.id
                WHERE c.name = 'Lider'
                AND u.deleted_at IS NULL
            """)
        result = session.execute(query).fetchall()
        return {nome: id for id, nome in result}


# 🔹 Função para salvar imagem
def save_image(uploaded_file, departamento):
    # Salva a imagem com o nome do departamento
    directory = "./src/img/departamento"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Atualiza para usar o nome do departamento
    image_path = os.path.join(directory, f"{departamento}.jpg")  # Salva com o nome do departamento
    imagem_pro = Image.open(uploaded_file)
    imagem_pro.save(image_path)

    return image_path  # Retorna o caminho da imagem salva


# Função para obter o caminho completo da imagem do usuário
def get_user_image_path(user_image):
    """
    Retorna o caminho completo da imagem do usuário.
    Se a imagem não existir, retorna um caminho padrão.
    """
    if user_image:
        image_path = os.path.join("./media/src/img/departamento", user_image)
        if os.path.exists(image_path):
            return image_path


def show_departamentos():
    # Inicializa valores padrão na sessão
    if "departamento_input" not in st.session_state:
        st.session_state.departamento_input = ""
    if "descricao_input" not in st.session_state:
        st.session_state.descricao_input = ""

    # Interface do Streamlit
    st.title("📌 Gerenciamento de Departamentos")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Cadastrar",
                                            "📋 Listar",
                                            "✏️ Editar/Excluir",
                                            "📊 Estatísticas",
                                            "📈 Análise Inteligente"])

    # Aba de Cadastro
    with tab1:
        st.header("📌 Cadastro de Departamentos")

        with st.form("form_cadastro_departamento", clear_on_submit=True, border=True):
            departamento = st.text_input("Nome do Departamento", value=st.session_state.departamento_input, key="departamento_key")
            lideres = obter_nomes_lideres()  # Chama a função para obter a lista de nomes

            if not lideres:
                st.warning("⚠️ Nenhum pastor cadastrado")
                responsavel_id = None
            else:
                # Selectbox com nomes
                nome_responsavel = st.selectbox(
                    "Selecione o Pastor Responsável*",
                    options=list(lideres.keys()),
                    index=None,
                    placeholder="Escolha um pastor..."
                )

                # Obter ID correspondente
                responsavel_id = lideres.get(nome_responsavel) if nome_responsavel else None

            descricao = st.text_area("Descrição", value=st.session_state.descricao_input, key="descricao_key")

            imagem_key = f"imagem_upload_{st.session_state.departamento_input}"
            imagem = st.file_uploader("Imagem do Departamento", type=["jpg", "jpeg", "png"], key=imagem_key)

            submitted = st.form_submit_button("✅ Cadastrar Departamento")

            if submitted:
                try:
                    session = Session()
                    img_path = save_image(imagem, departamento) if imagem else None
                    session.execute(text("""
                        INSERT INTO gestao_departamentos (departamento, descricao, img, created_dt, updated_dt, 
                        active_dt, name_lider) 
                        VALUES (:departamento, :descricao, :img, NOW(), NOW(), NOW(), :name_lider);
                    """), {"departamento": departamento, "descricao": descricao, "img": img_path, "name_lider": responsavel_id})
                    session.commit()

                    # Resetar valores corretamente
                    st.session_state.departamento_input = ""
                    st.session_state.descricao_input = ""
                    st.session_state["imagem_upload_key"] = f"imagem_upload_{departamento}_reset"

                    st.success("🎉 Departamento cadastrado com sucesso!")
                    st.balloons()

                except Exception as e:
                    st.error(f"Erro ao cadastrar departamento: {e}")
                finally:
                    session.close()

    # 📋 **Aba de Listagem**
    with tab2:
        st.header("📋 Lista de Departamentos")
        try:
            with engine.connect() as connection:
                df = pd.read_sql("SELECT * FROM gestao_departamentos", connection)
            if df.empty:
                st.info("⚠️ Nenhum departamento cadastrado.")
            else:
                st.dataframe(df)
        except Exception as e:
            st.error(f"Erro ao buscar departamentos: {e}")

    # ✏️ **Aba de Edição e Exclusão**
    with tab3:
        st.header("✏️ Editar ou Excluir Departamento")
        try:
            with engine.connect() as connection:
                df = pd.read_sql("SELECT * FROM gestao_departamentos", connection)
            if df.empty:
                st.info("⚠️ Nenhum departamento cadastrado.")
            else:
                departamento_selecionado = st.selectbox("Selecione o departamento", df["departamento"])
                departamento_info = df[df["departamento"] == departamento_selecionado].iloc[0]
                nova_descricao = st.text_area("Nova Descrição", departamento_info["descricao"])

                if st.button("💾 Salvar Alterações"):
                    try:
                        session = Session()
                        session.execute(text("""
                            UPDATE gestao_departamentos 
                            SET descricao=:descricao, updated_dt=NOW() 
                            WHERE departamento=:departamento
                        """), {"descricao": nova_descricao, "departamento": departamento_selecionado})
                        session.commit()
                        st.success("✅ Departamento atualizado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao atualizar departamento: {e}")
                    finally:
                        session.close()

                if st.button("❌ Excluir Departamento"):
                    try:
                        session = Session()
                        session.execute(text("DELETE FROM gestao_departamentos WHERE departamento=:departamento"),
                                        {"departamento": departamento_selecionado})
                        session.commit()
                        st.success("❌ Departamento removido com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao excluir departamento: {e}")
                    finally:
                        session.close()
        except Exception as e:
            st.error(f"Erro ao buscar departamentos: {e}")

    # 📊 **Aba de Estatísticas de Departamentos**
    with tab4:
        st.header("📊 Estatísticas de Departamentos")
        with Session() as session:
            # Consultas para obter estatísticas
            total_departamentos = session.execute(
                text("SELECT COUNT(*) FROM gestao_departamentos WHERE active_dt IS NOT NULL")).scalar() or 0
            departamentos_ativos = session.execute(text(
                "SELECT COUNT(*) FROM gestao_departamentos WHERE active_dt IS NOT NULL AND active_dt <= NOW()")).scalar() or 0
            departamentos_inativos = total_departamentos - departamentos_ativos

        # Exibição das métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Departamentos", total_departamentos)
        with col2:
            st.metric("Departamentos Ativos", departamentos_ativos)
        with col3:
            st.metric("Departamentos Inativos", departamentos_inativos)

        # Gráfico de barras para Departamentos Ativos vs Inativos
        fig = px.bar(
            x=["Ativos", "Inativos"],
            y=[departamentos_ativos, departamentos_inativos],
            title="Departamentos Ativos vs Inativos",
            labels={"x": "Status", "y": "Quantidade"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Listagem de departamentos ativos
        st.subheader("📋 Lista de Departamentos Ativos")
        with Session() as session:
            departamentos = session.execute(text("""
                SELECT id, departamento, descricao, name_lider 
                FROM gestao_departamentos 
                WHERE active_dt IS NOT NULL AND active_dt <= NOW()
            """)).fetchall()

            if not departamentos:
                st.info("⚠️ Nenhum departamento ativo encontrado.")
            else:
                df = pd.DataFrame(departamentos, columns=["ID", "Departamento", "Descrição", "Líder"])
                st.dataframe(df)

    # 📈 **Aba de Análise Inteligente de Departamentos**
    with tab5:
        st.header("📈 Análise Inteligente de Departamentos")
        st.subheader("📖 Narrativa Gerada Automaticamente")

        # Carregar dados dos departamentos
        with Session() as session:
            departamentos = session.query(GestaoDepartamentos).all()  # Consultar a tabela gestao_departamentos

            # Formatar dados para a LLM
            dados_llm = []
            for departamento in departamentos:
                dados_llm.append(f"""
                    Nome do Departamento: {departamento.departamento}
                    Descrição: {departamento.descricao}
                    Líder: {departamento.name_lider}
                    Status: {'Ativo' if departamento.active_dt and departamento.active_dt <= datetime.now() else 'Inativo'}
                    Data de Criação: {departamento.created_dt.strftime('%d/%m/%Y %H:%M:%S')}
                    Última Atualização: {departamento.updated_dt.strftime('%d/%m/%Y %H:%M:%S')}
                """)
            dados_formatados = "\n\n".join(dados_llm) if dados_llm else "Nenhum departamento cadastrado"

        # Sistema de prompt com dados dinâmicos
        system_prompt = f'''
        Você é MESTRE BÍBLIA, especialista em análise de departamentos da igreja Recomeçar.
        Suas respostas devem ser diretas e focadas em análise dos dados fornecidos sobre departamentos.

        Regras:
        1. Cumprimente o usuário da mesma forma que ele te cumprimentou (ex: "Bom dia", "Olá").
        2. Após o cumprimento, pergunte diretamente: "O que você gostaria de analisar hoje?".
        3. Seu cumprimento será somente na primeira interação com o usuário para não ficar repetitivo.
        4. Use os dados abaixo APENAS quando necessário para responder perguntas específicas do usuário.
        5. Não liste todos os departamentos disponíveis automaticamente, a menos que o usuário peça.
        6. Para perguntas sobre liderança ou descrições, use os dados fornecidos.

        Dados dos Departamentos:
        {dados_formatados}
        '''

        # Set a default model
        if "deepseek_model" not in st.session_state:
            st.session_state["deepseek_model"] = "deepseek-ai/deepseek-r1"

        # Interface do chat
        if "massages_dep" not in st.session_state:
            st.session_state.massages_dep = []

        # Contêiner para o histórico de mensagens
        chat_container = st.container()

        # Exibir histórico de mensagens dentro do contêiner
        with chat_container:
            for message in st.session_state.massages_dep:
                with st.chat_message(message["role"], avatar=get_user_image_path(message.get("avatar"))):
                    st.markdown(message["content"])

        # Campo de entrada fixo na parte inferior
        prompt = st.chat_input("Digite sua pergunta aqui...", key="chat_input")

        def clear_chat_history():
            st.session_state.massages_fin = [{
                "role": "assistant", "content": 'Olá! Sou o MESTRE BÍBLIA, pronto para ajudá-lo a compreender as '
                                                'análises sobre os departamentos da igreja.'}]

        st.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

        # Processar nova mensagem
        if prompt:
            # Adicionar mensagem do usuário
            st.session_state.massages_dep.append(
                {"role": "user", "content": prompt, "avatar": "user_image_placeholder"})
            with chat_container:
                with st.chat_message("user", avatar=get_user_image_path("user_image_placeholder")):
                    st.markdown(prompt)

            # Gerar resposta com replicate.stream
            with chat_container:
                with st.chat_message("assistant"):
                    try:
                        # Montar o full_prompt combinando o system_prompt e a pergunta do usuário
                        full_prompt = f"{system_prompt}\n\nPergunta do usuário: {prompt}"

                        # Stream da resposta usando DeepSeek-R1
                        full_response = ""
                        stream = replicate.stream(
                            st.session_state["deepseek_model"],
                            input={
                                "top_p": 1,
                                "prompt": full_prompt,
                                "max_tokens": 300,
                                "temperature": 0.1,
                                "presence_penalty": 0,
                                "frequency_penalty": 0
                            },
                        )

                        # Exibir a resposta em streaming
                        with st.spinner("Gerando análise..."):
                            response_container = st.empty()
                            for event in stream:
                                full_response += str(event)
                                clean_response = re.sub(r"<think>.*?</think>", "", full_response,
                                                        flags=re.DOTALL).strip()
                                response_container.markdown(clean_response)

                        # Salvar a resposta completa no histórico
                        st.session_state.massages_dep.append({"role": "assistant", "content": clean_response})

                    except Exception as e:
                        st.error(f"Erro ao gerar análise: {str(e)}")

    # Aplicar estilo aos cards 📌
    style_metric_cards(
        background_color="#008000",  # verde
        border_left_color="#FFFFFF",
        border_color="#000000",
        box_shadow="#FFFFFF"
    )
