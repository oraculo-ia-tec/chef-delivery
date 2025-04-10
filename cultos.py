import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from datetime import time
from enum import Enum
from streamlit_extras.metric_cards import style_metric_cards
from key_config import DATABASE_URL
from pydantic import BaseModel
import qrcode
import re
import os
import replicate
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    Text,
    DECIMAL,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Time,
    Date,
    func,
    text
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


# Criando conexão com o banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


class DiaCulto(Enum):
    segunda = 'Segunda'
    terca = 'Terca'
    quarta = 'Quarta'
    quinta = 'Quinta'
    sexta = 'Sexta'
    sabado = 'Sabado'
    domingo = 'Domingo'


# Definição da classe Culto
class Culto(Base):
    __tablename__ = 'oraculo_culto'  # Nome da tabela no banco de dados

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # ID do culto
    nome_culto = Column(String(255), nullable=False)  # Nome do culto
    nome_pregador = Column(String(255), nullable=False)  # Nome do pregador
    titulo_pregacao = Column(String(255), nullable=False)  # Título da pregação
    diaconato = Column(String(255), nullable=True)  # Diaconato
    grupo_louvor = Column(String(255), nullable=True)  # Grupo de louvor
    dia_culto = DiaCulto
    hora_inicio = Column(Time, nullable=False)  # Hora de início
    hora_fim = Column(Time, nullable=False)  # Hora de fim
    pastor_responsavel = Column(BigInteger, ForeignKey('oraculo_user.id'), nullable=True)  # ID do pastor responsável
    departamento_infantil = Column(Boolean, default=False)  # Booleano para indicar se haverá departamento infantil
    link_dizimo = Column(String(500), nullable=True)  # Link para pagamento de dízimo
    link_oferta = Column(String(500), nullable=True)  # Link para pagamento de oferta
    qrcode_dizimo = Column(String(500), nullable=True)  # QR Code para pagamento de dízimo
    qrcode_oferta = Column(String(500), nullable=True)  # QR Code para pagamento de oferta

    # Relacionamentos
    pastor = relationship("OraculoUser", back_populates="cultos")  # Relacionamento com o pastor


class OraculoUser(Base):
    __tablename__ = "oraculo_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # ID do usuário
    name = Column(String(100), nullable=False)  # Nome do usuário
    cpf_cnpj = Column(String(20))  # CPF ou CNPJ do usuário
    email = Column(String(254))  # E-mail do usuário
    whatsapp = Column(String(15))  # Número de WhatsApp do usuário
    endereco = Column(String(255))  # Endereço do usuário
    cep = Column(String(10))  # Código postal
    bairro = Column(String(100))  # Bairro do usuário
    cidade = Column(String(100))  # Cidade do usuário
    username = Column(String(50))  # Nome de usuário
    password = Column(String(128))  # Senha do usuário
    image = Column(String(100))  # Caminho da imagem do usuário
    created_at = Column(Date)  # Data de criação do registro
    created_time = Column(Time)  # Hora de criação do registro
    deleted_at = Column(Date)  # Data de exclusão do registro, se aplicável
    deleted_time = Column(Time)  # Hora de exclusão do registro, se aplicável
    cargo_id = Column(BigInteger)  # ID do cargo do usuário
    decisao = Column(String(50))  # Decisão do usuário
    culto_id = Column(BigInteger)  # ID do culto associado
    estado_civil = Column(String(20))  # Estado civil do usuário
    filhos = Column(Integer)  # Número de filhos
    cultos = relationship("Culto", back_populates="pastor")


class GestaoDepartamentos(Base):
    __tablename__ = "gestao_departamentos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # ID do departamento
    created_dt = Column(DateTime(6))  # Data de criação do registro
    updated_dt = Column(DateTime(6))  # Data da última atualização
    active_dt = Column(DateTime)  # Data de ativação do departamento
    departamento = Column(String(100), nullable=False)  # Nome do departamento
    descricao = Column(Text)  # Descrição do departamento
    img = Column(String(100))  # Caminho da imagem representativa do departamento
    name_lider = Column(String(255))  # Nome do líder do departamento


# Inicializa os campos do culto no session_state se não existirem
campos_culto = [
    "nome_culto", "nome_pregador", "titulo_pregacao", "diaconato", "grupo_louvor",
    "dia_culto", "hora_inicio", "hora_fim",
    "novo_membro_id", "pastor_responsavel", "departamento_infantil"
]
for campo in campos_culto:
    if campo not in st.session_state:
        st.session_state[campo] = ""


def obter_dizimos():
    with engine.connect() as connection:
        query = text("SELECT valor_total FROM dizimo")
        result = connection.execute(query)
        cargos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return cargos


def obter_ofertas():
    with engine.connect() as connection:
        query = text("SELECT valor_total FROM oferta")
        result = connection.execute(query)
        cargos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return cargos


def obter_cargos():
    with engine.connect() as connection:
        query = text("SELECT nome FROM oraculo_cargo")
        result = connection.execute(query)
        cargos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return cargos


def obter_pastor_responsavel():
    with engine.connect() as connection:
        query = text("""
            SELECT u.id, u.name 
            FROM oraculo_user u 
            JOIN oraculo_cargo c ON u.cargo_id = c.id 
            WHERE c.name = 'Pastor'
        """)
        result = connection.execute(query)
        # Extrai os IDs e nomes dos pastores em uma lista de tuplas (id, name)
        pastor_responsavel = [(row[0], row[1]) for row in result.fetchall()]
    return pastor_responsavel


def obter_departamento():
    with engine.connect() as connection:
        query = text("SELECT departamento FROM gestao_departamentos")
        result = connection.execute(query)
        departamentos = [row[0] for row in result.fetchall()]  # Extrai apenas os nomes dos cargos
    return departamentos


# Função para obter o caminho completo da imagem do usuário
def get_user_image_path(user_image):
    """
    Retorna o caminho completo da imagem do usuário.
    Se a imagem não existir, retorna um caminho padrão.
    """
    if user_image:
        image_path = os.path.join("./media/src/img/membro", user_image)
        if os.path.exists(image_path):
            return image_path


def obter_diaconos():
    """Retorna lista de diaconos (id, nome) do banco de dados"""
    with get_db_session() as session:
        query = text("""
            SELECT u.id, u.name 
            FROM oraculo_user u
            JOIN oraculo_cargo c ON u.cargo_id = c.id
            WHERE c.name = 'Diácono'
            AND u.deleted_at IS NULL
        """)
        result = session.execute(query).fetchall()
        return {nome: id for id, nome in result}  # Dicionário {Nome: ID}


def atualizar_culto(culto_id, dados_atualizados):
    try:
        with Session() as session:
            culto = session.get(Culto, culto_id)
            for key, value in dados_atualizados.items():
                setattr(culto, key, value)
            session.commit()
            return True
    except Exception as e:
        print(f"Erro ao atualizar culto: {e}")
        return False


def deletar_culto(culto_id):
    try:
        with Session() as session:
            culto = session.get(Culto, culto_id)
            session.delete(culto)
            session.commit()
            return True
    except Exception as e:
        print(f"Erro ao deletar culto: {e}")
        return False


# Função para gerar e salvar QR Codes
def gerar_qrcode(url, caminho_salvar, nome_arquivo):
    """
    Gera um QR Code a partir de uma URL e salva no caminho especificado.
    Retorna o caminho completo do arquivo salvo ou None se a URL for inválida.
    """
    if not url:
        return None  # Não gera QR Code se a URL estiver vazia

    # Cria o diretório, se não existir
    os.makedirs(caminho_salvar, exist_ok=True)

    # Cria o QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Cria a imagem do QR Code
    img = qr.make_image(fill_color="black", back_color="white")

    # Salva a imagem no caminho especificado
    caminho_completo = os.path.join(caminho_salvar, nome_arquivo)
    img.save(caminho_completo)

    return caminho_completo


def cadastrar_culto():
    # Interface do Streamlit
    st.title("🙏 Gerenciamento de Cultos")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Cadastrar",
                                            "📋 Listar",
                                            "✏️ Editar/Excluir",
                                            "📊 Estatísticas",
                                            "📈 Análise Inteligente"])

    # ✏️ **Aba de Cadastro de Culto**
    with tab1:
        st.header("Cadastrar Novo Culto")
        with st.form(key='form_cadastro_culto', clear_on_submit=True, border=True):

            # Criar duas colunas
            col1, col2 = st.columns(2)

            # Coluna 1
            with col1:
                nome_culto = st.text_input("Nome do Culto")
                # Exibir apenas os nomes dos dias no selectbox
                dia_culto_opcoes = [dia.value for dia in DiaCulto]  # Lista com os nomes dos dias
                dia_culto_selecionado = st.selectbox('Selecione o dia do culto: ', dia_culto_opcoes)
                hora_inicio = st.time_input("Hora de Início", value=time(19, 0))
                diaconos = obter_diaconos()
                diaconato = ', '.join(st.multiselect("Diáconos:", diaconos))
                grupo_louvor = st.text_input("Grupo de Louvor")

            # Coluna 2
            with col2:
                nome_pregador = st.text_input("Nome do Pregador")
                titulo_pregacao = st.text_input("Título da Pregação")
                hora_fim = st.time_input("Hora de Término", value=time(20, 30))

                # Obter os pastores responsáveis
                pastores = obter_pastor_responsavel()
                nomes_pastores = [pastor[1] for pastor in pastores]
                pastor_selecionado = st.selectbox("Pastor Responsável do Culto", nomes_pastores)
                id_pastor_responsavel = next(pastor[0] for pastor in pastores if pastor[1] == pastor_selecionado)

                departamento_infantil = st.radio("Terá departamento infantil?", ("Sim", "Não"))
                departamento_infantil_bool = True if departamento_infantil == "Sim" else False

            # Links e QR Codes
            st.expander("Links e QR Codes")
            link_dizimo = st.text_input("Link para Pagamento de Dízimo") or None
            link_oferta = st.text_input("Link para Pagamento de Oferta") or None

            submitted = st.form_submit_button("✅ Cadastrar Culto")
            if submitted:
                try:
                    # Diretórios para salvar os QR Codes
                    os.makedirs("./media/src/img/dizimos", exist_ok=True)
                    os.makedirs("./media/src/img/ofertas", exist_ok=True)

                    # Gerar e salvar QR Codes apenas se os links forem fornecidos
                    qrcode_dizimo_path = None
                    qrcode_oferta_path = None

                    if link_dizimo:
                        qrcode_dizimo_path = gerar_qrcode(link_dizimo, "./media/src/img/dizimos",
                                                          f"{nome_culto}_dizimo.png")

                    if link_oferta:
                        qrcode_oferta_path = gerar_qrcode(link_oferta, "./media/src/img/ofertas",
                                                          f"{nome_culto}_oferta.png")

                    # Garantir que o dia do culto esteja em minúsculas
                    dia_culto_lower = dia_culto_selecionado.lower()  # Usar a variável correta

                    # Salvar os dados no banco de dados
                    with Session() as session:
                        session.execute(
                            text("""
                                INSERT INTO oraculo_culto (
                                    nome_culto, nome_pregador, titulo_pregacao, diaconato, grupo_louvor,
                                    dia_culto, hora_inicio, hora_fim, pastor_responsavel, departamento_infantil,
                                    link_dizimo, link_oferta, qrcode_dizimo, qrcode_oferta
                                )
                                VALUES (
                                    :nome_culto, :nome_pregador, :titulo_pregacao, :diaconato, :grupo_louvor,
                                    :dia_culto, :hora_inicio, :hora_fim, :pastor_responsavel, :departamento_infantil,
                                    :link_dizimo, :link_oferta, :qrcode_dizimo, :qrcode_oferta
                                )
                            """),
                            {
                                "nome_culto": nome_culto,
                                "nome_pregador": nome_pregador,
                                "titulo_pregacao": titulo_pregacao,
                                "diaconato": diaconato,
                                "grupo_louvor": grupo_louvor,
                                "dia_culto": dia_culto_lower,  # Usar a variável correta
                                "hora_inicio": hora_inicio,
                                "hora_fim": hora_fim,
                                "pastor_responsavel": id_pastor_responsavel,
                                "departamento_infantil": departamento_infantil_bool,
                                "link_dizimo": link_dizimo,
                                "link_oferta": link_oferta,
                                "qrcode_dizimo": qrcode_dizimo_path,
                                "qrcode_oferta": qrcode_oferta_path
                            }
                        )
                        session.commit()
                        st.success("🎉 Culto cadastrado com sucesso!")
                        st.balloons()
                except Exception as e:
                    st.error(f"🚨 Erro ao cadastrar culto: {e}")

    # ✏️ **Aba de Listagem de Cultos**
    with tab2:
        st.header("📖 Listar Cultos")

        # Consulta ao banco de dados
        with Session() as session:
            cultos = session.query(Culto).all()

        # Verifica se há cultos cadastrados
        if not cultos:
            st.warning("⚠️ Nenhum culto cadastrado.")
        else:
            # Converte os dados dos cultos para um DataFrame
            cultos_data = [
                {
                    "ID": culto.id,
                    "Nome do Culto": culto.nome_culto,
                    "Pregador": culto.nome_pregador,
                    "Título da Pregação": culto.titulo_pregacao,
                    "Diáconos": culto.diaconato,
                    "Grupo de Louvor": culto.grupo_louvor,
                    "Dia do Culto": str(culto.dia_culto).capitalize(),
                    "Hora de Início": culto.hora_inicio.strftime('%H:%M'),
                    "Hora de Término": culto.hora_fim.strftime('%H:%M'),
                    "Pastor Responsável": culto.pastor_responsavel,
                    "Departamento Infantil": "Sim" if culto.departamento_infantil else "Não",
                    "Link Dízimo": culto.link_dizimo,
                    "QR Code Dízimo": culto.qrcode_dizimo,
                    "Link Oferta": culto.link_oferta,
                    "QR Code Oferta": culto.qrcode_oferta,
                }
                for culto in cultos
            ]

            df = pd.DataFrame(cultos_data)

            # Pesquisa por nome do culto
            pesquisa = st.chat_input("🔍 Pesquisar por nome do culto (digite os 3 primeiros caracteres)")
            if pesquisa and len(pesquisa) >= 3:
                df = df[df["Nome do Culto"].str.lower().str.startswith(pesquisa.lower(), na=False)]

            # Exibe o DataFrame
            st.dataframe(df)

            # Exibir QR Codes separadamente, se necessário
            if not df.empty:
                st.subheader("Visualizar QR Codes")
                culto_selecionado = st.selectbox("Selecione um culto:", df["Nome do Culto"])
                culto = next((c for c in cultos if c.nome_culto == culto_selecionado), None)

                if culto:
                    # Configuração do tamanho do QR Code (opcional)
                    qr_code_width = 300  # Largura em pixels (ajuste conforme necessário)

                    if culto.qrcode_dizimo:
                        st.image(culto.qrcode_dizimo, caption="QR Code para Dízimo", width=200,
                                 use_container_width=True)
                    if culto.qrcode_oferta:
                        st.image(culto.qrcode_oferta, caption="QR Code para Oferta", width=200,
                                 use_container_width=True)

    # ✏️ **Aba de Edição/Exclusão de Cultos**
    with tab3:
        st.header("✏️ Editar ou Excluir Cultos")

        with Session() as session:
            cultos = session.query(Culto).all()

        if not cultos:
            st.warning("⚠️ Nenhum culto cadastrado.")
        else:
            cultos_nomes = [culto.nome_culto for culto in cultos]
            culto_selecionado = st.selectbox("Escolha o culto:", cultos_nomes, key="culto_editar")
            culto_atual = next((c for c in cultos if c.nome_culto == culto_selecionado), None)

            if culto_atual:
                novo_nome_culto = st.text_input("Nome do Culto", value=culto_atual.nome_culto, key="novo_nome_culto")
                novo_nome_pregador = st.text_input("Nome do Pregador", value=culto_atual.nome_pregador,
                                                   key="novo_nome_pregador")
                novo_titulo_pregacao = st.text_input("Título da Pregação", value=culto_atual.titulo_pregacao,
                                                     key="novo_titulo_pregacao")
                novo_diaconato = st.text_input("Diácono Responsável", value=culto_atual.diaconato, key="novo_diaconato")
                novo_grupo_louvor = st.text_input("Grupo de Louvor", value=culto_atual.grupo_louvor,
                                                  key="novo_grupo_louvor")
                novo_dia_culto = st.selectbox(
                    "Dia do Culto", DiaCulto)
                nova_hora_inicio = st.time_input("Hora de Início", value=culto_atual.hora_inicio,
                                                 key="nova_hora_inicio")
                nova_hora_fim = st.time_input("Hora de Término", value=culto_atual.hora_fim, key="nova_hora_fim")
                novo_pastor_responsavel = st.number_input("ID do Pastor Responsável", min_value=1,
                                                          value=culto_atual.pastor_responsavel, step=1,
                                                          key="novo_pastor_responsavel")
                novo_departamento_infantil = st.checkbox("Departamento Infantil Ativo?",
                                                         value=bool(culto_atual.departamento_infantil),
                                                         key="novo_departamento_infantil")

                # Links e QR Codes
                st.subheader("Links e QR Codes")
                novo_link_dizimo = st.text_input("Link para Pagamento de Dízimo", value=culto_atual.link_dizimo,
                                                 key="novo_link_dizimo")
                novo_link_oferta = st.text_input("Link para Pagamento de Oferta", value=culto_atual.link_oferta,
                                                 key="novo_link_oferta")

                if st.button("💾 Salvar Alterações"):
                    try:
                        # Diretórios para salvar os QR Codes
                        os.makedirs("./media/src/img/dizimos", exist_ok=True)
                        os.makedirs("./media/src/img/ofertas", exist_ok=True)

                        # Salvar novos QR Codes se os links forem alterados
                        novo_qrcode_dizimo = salvar_qrcode(novo_link_dizimo, "./media/src/img/dizimos",
                                                           f"{novo_nome_culto}_dizimo.png")
                        novo_qrcode_oferta = salvar_qrcode(novo_link_oferta, "./media/src/img/ofertas",
                                                           f"{novo_nome_culto}_oferta.png")

                        dados_atualizados = {
                            "nome_culto": novo_nome_culto,
                            "nome_pregador": novo_nome_pregador,
                            "titulo_pregacao": novo_titulo_pregacao,
                            "diaconato": novo_diaconato,
                            "grupo_louvor": novo_grupo_louvor,
                            "dia_culto": novo_dia_culto.lower(),
                            # Convertendo para minúsculas para compatibilidade com ENUM
                            "hora_inicio": nova_hora_inicio,
                            "hora_fim": nova_hora_fim,
                            "pastor_responsavel": novo_pastor_responsavel,
                            "departamento_infantil": novo_departamento_infantil,
                            "link_dizimo": novo_link_dizimo,
                            "link_oferta": novo_link_oferta,
                            "qrcode_dizimo": novo_qrcode_dizimo or culto_atual.qrcode_dizimo,
                            # Mantém o valor antigo se não houver novo QR Code
                            "qrcode_oferta": novo_qrcode_oferta or culto_atual.qrcode_oferta
                            # Mantém o valor antigo se não houver novo QR Code
                        }
                        atualizar_culto(culto_atual.id, dados_atualizados)
                        st.success("✅ Culto atualizado com sucesso!")
                    except Exception as e:
                        st.error(f"🚨 Erro ao salvar alterações: {e}")

                if st.button("❌ Excluir Culto"):
                    try:
                        deletar_culto(culto_atual.id)
                        st.success("✅ Culto excluído com sucesso!")
                    except Exception as e:
                        st.error(f"🚨 Erro ao excluir o culto: {e}")
            else:
                st.warning("⚠️ Culto não encontrado.")

    # Aba de Estatísticas
    with tab4:
        st.header("📊 Estatísticas de Cultos")
        with Session() as session:
            # Usando o método correto para contar e somar valores
            total_cultos = session.execute(text("SELECT COUNT(*) FROM oraculo_culto")).scalar() or 0
            total_dizimos = session.execute(text("SELECT SUM(valor_total) FROM dizimo")).scalar() or 0
            total_ofertas = session.execute(text("SELECT SUM(valor_total) FROM oferta")).scalar() or 0
            total_novos_membros = session.execute(text("SELECT COUNT(*) FROM oraculo_user")).scalar() or 0

        # Ajustando a exibição das métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Cultos", total_cultos)
        with col2:
            st.metric("Total de Dízimos", f"R$ {total_dizimos:,.2f}")
        with col3:
            st.metric("Total de Ofertas", f"R$ {total_ofertas:,.2f}")
        with col4:
            st.metric("Novos Membros", total_novos_membros)

        # Criando gráfico de barras para Dízimos e Ofertas
        fig = px.bar(x=["Dízimos", "Ofertas"], y=[total_dizimos, total_ofertas],
                     title="Dízimos e Ofertas", labels={"x": "Tipo", "y": "Valor Total"})
        st.plotly_chart(fig, use_container_width=True)

    # 📈 **Aba de Análise Inteligente**
    with tab5:
        st.header("📈 Análise Inteligente - Cultos")

        # Carregar dados dos cultos
        with get_db_session() as session:
            cultos = session.query(Culto).all()  # Consultar a tabela oraculo_culto

            # Formatar dados para a LLM
            dados_llm = []
            for culto in cultos:
                dados_llm.append(f"""
                    Nome do Culto: {culto.nome_culto}
                    Pregador: {culto.nome_pregador}
                    Título da Pregação: {culto.titulo_pregacao}
                    Diaconato: {culto.diaconato}
                    Grupo de Louvor: {culto.grupo_louvor}
                    Dia do Culto: {culto.dia_culto}
                    Horário: {culto.hora_inicio.strftime('%H:%M')} - {culto.hora_fim.strftime('%H:%M')}
                    Pastor Responsável: {culto.pastor_responsavel}  # Aqui você pode fazer uma nova consulta para obter o nome do pastor
                    Departamento Infantil: {culto.departamento_infantil}  # Da mesma forma, consulte o nome do departamento
                """)
            dados_formatados = "\n\n".join(dados_llm) if dados_llm else "Nenhum culto cadastrado"

            # Sistema de prompt com dados dinâmicos
            system_prompt = f'''
                Você é o MESTRE BÍBLIA, especialista em análise de dados dos cultos da igreja Comunidade Cristã Recomeçar.
                Suas respostas devem ser diretas e focadas em análise dos dados fornecidos sobre os cultos da igreja.
                Você não prolongará suas respostas para mais de 150 tokens.
                Não responda perguntas fora do contexto e se o usuário insistir não responda nenhuma pergunta sobre outro 
                assunto.

                Regras:
                    1. Responda com base nos dados fornecidos da igreja sobre os cultos.
                    2. Cumprimente o usuário e pergunte o nome dele. 
                        Exemplo 1 da primeira interação:
                            Usuário:  Ola bom dia , você tem informações sobre a Recomeçar?
                            Mestre Bíblia: Olá, boa tarde! Sim, tenho informações sobre a Comunidade Cristã Recomeçar. 
                            Como você se chama?
                            Usuário: Meu nome é william eustaquio gomes DA Silva
                            Mestre Bíblia: Olá, William! Muito prazer em conhecê-lo. 
                            A Recomeçar foi fundada em 2005 pelo pr. Marciano e sua esposa, Maria dos Santos. Em 2006, 
                            o pastor Ronaldo Santos assumiu a liderança e mudou o nome para Comunidade Cristã Recomeçar. 
                            Em 2017, a igreja se mudou para sua sede atual na Av. Dr. João Augusto Fonseca e Silva, 387, 
                            no bairro Novo Eldorado, em Contagem/MG. Você gostaria de saber algo mais específico?
                        Exemplo 2 da primeira interação:
                            Usuário:  ola boa tarde
                            Mestre Bíblia: Olá, boa tarde!Como você se chama?
                            Usuário: Meu nome é william eustaquio gomes DA Silva
                            Mestre Bíblia: Olá, William! Muito prazer em conhecê-lo, como deseja receber a análise dos 
                            cultos da igreja Comunidade Cristã Recomeçar?
                        Exemplo 3 da primeira interação:
                            Usuário:  ola boa noite
                            Mestre Bíblia: Olá, boa noite!Como você se chama?
                            Usuário: Meu nome é william eustaquio gomes DA Silva e o seu ?
                            Mestre Bíblia: Olá, William! Pode me chamar de MESTRE BÍBLIA, especialista em análise de dados 
                            dos cultos da igreja Comunidade Cristã Recomeçar. como deseja receber a análise?   

                    3. Prosiga a conversa normalmente focando somente em responder a análise de dados os cultos: 
                        {dados_formatados}.
                    4. Seja profissional nas suas respostas e nas análises e não erre.
                    5. Não liste todos os cultos automaticamente, a menos que o usuário peça.
                    6. Para perguntas sobre os cultos, faça análise cruzada entre as tabelas.  
                '''

        # Set a default model
        if "deepseek_model" not in st.session_state:
            st.session_state["deepseek_model"] = "deepseek-ai/deepseek-r1"

        # Interface do chat
        if "massages_cul" not in st.session_state:
            st.session_state.massages_cul = []

        # Contêiner para o histórico de mensagens
        chat_container = st.container()

        # Exibir histórico de mensagens dentro do contêiner
        with chat_container:
            for message in st.session_state.massages_cul:
                with st.chat_message(message["role"], avatar=get_user_image_path(message.get("avatar"))):
                    st.markdown(message["content"])

        # Campo de entrada fixo na parte inferior
        prompt = st.chat_input("Digite sua pergunta aqui...", key="chat_input")

        def clear_chat_history():
            st.session_state.massages_cul = [{
                "role": "assistant", "content": 'Olá! Sou o MESTRE BÍBLIA, pronto para ajudá-lo a compreender as '
                                                'análises sobre os cultos da igreja.'}]

        st.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

        # Processar nova mensagem
        if prompt:
            # Adicionar mensagem do usuário
            st.session_state.massages_cul.append(
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
                        st.session_state.massages_cul.append({"role": "assistant", "content": clean_response})

                    except Exception as e:
                        st.error(f"Erro ao gerar análise: {str(e)}")

    # Aplicar estilo aos cards 📌
    style_metric_cards(
        background_color="#008000",  # verde
        border_left_color="#FFFFFF",
        border_color="#000000",
        box_shadow="#FFFFFF"
    )