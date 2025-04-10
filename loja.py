import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px
import pandas as pd
from datetime import datetime
import os

from sqlalchemy import create_engine, Column, BigInteger, String, DateTime, Boolean, func, text, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from key_config import DATABASE_URL


# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Modelo da Categoria da Loja
class CategoriaLoja(Base):
    __tablename__ = 'categoria_loja'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=True)


# Modelo da Loja
class Loja(Base):
    __tablename__ = 'oraculo_loja'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    cnpj = Column(String(20), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    endereco = Column(String(255), nullable=True)
    cep = Column(String(10), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(50), nullable=True)
    status = Column(Boolean, nullable=True)
    user_id = Column(BigInteger, nullable=False)
    categoria_id = Column(BigInteger, nullable=True)  # Relacionamento com Categoria
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Funções para CRUD
def criar_loja(loja_dados):
    with Session() as session:
        nova_loja = Loja(**loja_dados)
        session.add(nova_loja)
        session.commit()
        return nova_loja.id


# Função corrigida para salvar a lojas corretamente
def salvar_loja(loja_dados):
    with Session() as session:
        nova_loja = Loja(**loja_dados)
        session.add(nova_loja)
        session.commit()
        return nova_loja.id  # Retorna o ID da lojas criada


def listar_lojas():
    with Session() as session:
        return session.query(Loja).all()


def atualizar_loja(loja_id, dados_atualizados):
    with Session() as session:
        loja = session.get(Loja, loja_id)
        for key, value in dados_atualizados.items():
            setattr(loja, key, value)
        session.commit()


def excluir_loja(loja_id):
    with Session() as session:
        loja = session.get(Loja, loja_id)
        session.delete(loja)
        session.commit()


if 'loja_nome' not in st.session_state:
    st.session_state.loja_nome = ""
if 'loja_descricao' not in st.session_state:
    st.session_state.loja_descricao = ""
if 'loja_cnpj' not in st.session_state:
    st.session_state.loja_cnpj = ""
if 'loja_telefone' not in st.session_state:
    st.session_state.loja_telefone = ""
if 'loja_email' not in st.session_state:
    st.session_state.loja_email = ""
if 'loja_endereco' not in st.session_state:
    st.session_state.loja_endereco = ""
if 'loja_cep' not in st.session_state:
    st.session_state.loja_cep = ""
if 'loja_bairro' not in st.session_state:
    st.session_state.loja_bairro = ""
if 'loja_cidade' not in st.session_state:
    st.session_state.loja_cidade = ""
if 'loja_estado' not in st.session_state:
    st.session_state.loja_estado = ""
if 'loja_status' not in st.session_state:
    st.session_state.loja_status = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""


# Diretório de imagens das lojas
IMAGE_DIR_LOJA = "./src/img/lojas"
EXCEL_FILE_LOJA = "lojas.xlsx"


# Criar diretório se não existir
os.makedirs(IMAGE_DIR_LOJA, exist_ok=True)


# Criar arquivo Excel se não existir
if not os.path.exists(EXCEL_FILE_LOJA):
    pd.DataFrame(columns=[
        "Nome",
        "Descrição",
        "CNPJ",
        "Telefone",
        "Email",
        "Endereço",
        "CEP",
        "Bairro",
        "Cidade",
        "Estado",
        "Estatus Loja"
    ]).to_excel(EXCEL_FILE_LOJA, index=False, sheet_name="Lojas", engine="openpyxl")


# 🔹 Função para obter categorias da lojas
def obter_lojas_por_categoria():
    """Obtém categorias de lojas e retorna um dicionário {Nome: ID}."""
    with engine.connect() as connection:
        query = text("SELECT id, nome FROM categoria_loja")
        result = connection.execute(query).fetchall()
        return {row[1]: row[0] for row in result}  # Retorna {Nome: ID}


# 🔹 Função para obter membros responsáveis
def obter_membros_por_cargo(cargos_desejados):
    """Obtém membros por cargo e retorna um dicionário {Nome: ID}."""
    with engine.connect() as connection:
        query = text("SELECT id, name FROM oraculo_user WHERE cargo_id IN :cargos")
        result = connection.execute(query, {'cargos': tuple(cargos_desejados)}).fetchall()
        return {row[1]: row[0] for row in result}  # Retorna {Nome: ID}


# Função para salvar dados das lojas no Excel
def salvar_dados_loja_em_excel():
    lojas_data = []
    for loja in st.session_state.lojas:  # Supondo que st.session_state.lojas armazene dados de lojas
        lojas_data.append({
            "Nome": loja.nome,
            "Descrição": loja.descricao,
            "CNPJ": loja.cnpj,
            "Telefone": loja.telefone,
            "Email": loja.email,
            "Endereço": loja.endereco,
            "CEP": loja.cep,
            "Bairro": loja.bairro,
            "Cidade": loja.cidade,
            "Estado": loja.estado,
            "Estatus Loja": "Ativa" if loja.status else "Inativa",
        })
    df_lojas = pd.DataFrame(lojas_data)
    df_lojas.to_excel(EXCEL_FILE_LOJA, index=False, sheet_name="Lojas", engine="openpyxl")


# Função para deletar lojas
def deletar_loja(loja_nome):
    """Remove uma lojas pelo nome e atualiza a planilha."""
    try:
        if loja_nome in [loja.nome for loja in st.session_state.lojas]:
            loja_removida = next((l for l in st.session_state.lojas if l.nome == loja_nome), None)

            if loja_removida:
                st.session_state.lojas.remove(loja_removida)  # Remove a lojas da lista

                # Verifica se há imagem associada e a remove do diretório
                if hasattr(loja_removida, "imagem") and loja_removida.imagem:
                    if os.path.exists(loja_removida.imagem):
                        os.remove(loja_removida.imagem)

                salvar_dados_loja_em_excel()  # Atualiza o Excel após remoção
                st.success(f"✅ Loja '{loja_nome}' removida com sucesso!")
            else:
                st.warning("⚠️ Loja não encontrada.")
        else:
            st.error("⚠️ Loja não encontrada na lista.")
    except Exception as e:
        st.error(f"🚨 Erro ao deletar a lojas: {e}")


def criar_loja():

    if "categorias_loja" not in st.session_state:
        st.session_state.categorias_loja = {}
    if "lojas" not in st.session_state:
        st.session_state.lojas = []

    # Interface do Streamlit
    st.title("🛒 Gerenciamento de Lojas")
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastrar", "📋 Listar", "✏️ Editar/Excluir", "📈 Estatísticas"])

    # Cadastro de Lojas
    with tab1:
        st.header("📌 Cadastro de Lojas")

        categorias = obter_lojas_por_categoria()  # Agora retorna {Nome: ID}
        responsaveis = obter_membros_por_cargo(["lider", "admin"])  # Agora retorna {Nome: ID}

        # 🔹 Cadastro de Categorias
        with st.expander("📂 Adicionar Categoria da Loja"):
            categoria_nome = st.text_input("Digite o nome da nova categoria:")
            categoria_descricao = st.text_input("Descrição: Simples")
            if st.button("✅ Cadastrar Categoria"):
                if categoria_nome.strip() and categoria_nome not in st.session_state.categorias_loja:
                    # Adiciona a categoria ao banco de dados
                    with Session() as session:
                        nova_categoria = CategoriaLoja(nome=categoria_nome, descricao=categoria_descricao)
                        session.add(nova_categoria)
                        session.commit()
                    st.session_state.categorias_loja[categoria_nome] = []
                    st.success(f"Categoria {categoria_nome} cadastrada!")
                else:
                    st.error("⚠️ Nome inválido ou categoria já existe.")

        with st.form("form_cadastro_loja", clear_on_submit=True, border=True):
            col1, col2 = st.columns(2)  # Cria duas colunas

            with col1:  # Campos na primeira coluna
                categoria_nome = st.selectbox("Selecione a Categoria", list(categorias.keys()))
                responsavel_nome = st.selectbox("Selecione o Responsável", list(responsaveis.keys()))
                nome_loja = st.text_input("📝 Nome da Loja")
                descricao = st.text_area("Descrição")
                cnpj = st.text_input("📄 CNPJ")
                status = st.selectbox("Status", options=["Ativa", "Inativa"])

            with col2:  # Campos na segunda coluna
                telefone = st.text_input("📞 Telefone")
                email = st.text_input("📧 Email")
                endereco = st.text_input("🏠 Endereço")
                cep = st.text_input("📬 CEP")
                bairro = st.text_input("🏘️ Bairro")
                cidade = st.text_input("🏙️ Cidade")
                estado = st.text_input("🌍 Estado")

            submitted = st.form_submit_button("✅ Cadastrar Loja")
            if submitted:
                loja_dados = {
                    "nome": nome_loja,
                    "descricao": descricao,
                    "cnpj": cnpj,
                    "telefone": telefone,
                    "email": email,
                    "endereco": endereco,
                    "cep": cep,
                    "bairro": bairro,
                    "cidade": cidade,
                    "estado": estado,
                    "status": status == "Ativa",
                    "user_id": responsaveis[responsavel_nome],  # Obtendo o ID correto
                    "categoria_id": categorias[categoria_nome]  # Obtendo o ID correto
                }
                try:
                    with Session() as session:
                        nova_loja = Loja(**loja_dados)
                        session.add(nova_loja)
                        session.commit()
                        st.success(f"Loja '{nome_loja}' foi cadastrada com sucesso!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Erro ao cadastrar a lojas: {e}")

    # Listagem de Lojas
    with tab2:
        st.header("📋 Lista de Lojas")
        with engine.connect() as connection:
            df = pd.read_sql("SELECT * FROM oraculo_loja", connection)  # Consulta à tabela de lojas
        if df.empty:
            st.info("⚠️ Ainda não foi cadastrado nenhuma lojas.")
        else:
            pesquisa = st.chat_input("🔍 Pesquisar por nome ou CNPJ (digite os 3 primeiros caracteres)")
            if pesquisa and len(pesquisa) >= 3:  # Verifica se a pesquisa tem pelo menos 3 caracteres
                # Filtrando o DataFrame para encontrar nomes ou CNPJ que começam com os caracteres digitados
                df = df[df["nome"].str.lower().str.startswith(pesquisa.lower(), na=False) |
                        df["cnpj"].str.startswith(pesquisa, na=False)]
            st.dataframe(df)

    # Edição e Exclusão de Lojas
    with tab3:
        st.header("✏️ Editar ou Excluir Lojas")
        lojas = listar_lojas()
        if not lojas:
            st.info("⚠️ Nenhuma lojas cadastrada.")
        else:
            loja_id = st.selectbox("Selecione a lojas", [loja.id for loja in lojas])
            loja = next(loja for loja in lojas if loja.id == loja_id)

            st.session_state.loja_nome = st.text_input("📝 Nome da Loja", loja.nome)
            st.session_state.loja_descricao = st.text_area("Descrição", loja.descricao)
            st.session_state.loja_cnpj = st.text_input("📄 CNPJ", loja.cnpj)
            st.session_state.loja_telefone = st.text_input("📞 Telefone", loja.telefone)
            st.session_state.loja_email = st.text_input("📧 Email", loja.email)
            st.session_state.loja_endereco = st.text_input("🏠 Endereço", loja.endereco)
            st.session_state.loja_cep = st.text_input("📬 CEP", loja.cep)
            st.session_state.loja_bairro = st.text_input("🏘️ Bairro", loja.bairro)
            st.session_state.loja_cidade = st.text_input("🏙️ Cidade", loja.cidade)
            st.session_state.loja_estado = st.text_input("🌍 Estado", loja.estado)

            if st.button("💾 Salvar Alterações"):
                dados_atualizados = {
                    "nome": st.session_state.loja_nome,
                    "descricao": st.session_state.loja_descricao,
                    "cnpj": st.session_state.loja_cnpj,
                    "telefone": st.session_state.loja_telefone,
                    "email": st.session_state.loja_email,
                    "endereco": st.session_state.loja_endereco,
                    "cep": st.session_state.loja_cep,
                    "bairro": st.session_state.loja_bairro,
                    "cidade": st.session_state.loja_cidade,
                    "estado": st.session_state.loja_estado,
                    "user_id": loja.user_id
                }
                atualizar_loja(loja_id, dados_atualizados)
                st.success("✅ Loja atualizada com sucesso!")

            if st.button("❌ Excluir Loja"):
                excluir_loja(loja_id)
                st.success("❌ Loja removida com sucesso!")

    # Estatísticas das Lojas
    with tab4:
        st.header("📈 Estatísticas das Lojas")
        with Session() as session:
            total_lojas = session.query(func.count(Loja.id)).scalar()
            lojas_ativas = session.query(func.count(Loja.id)).filter(Loja.status == True).scalar()
            lojas_inativas = total_lojas - lojas_ativas
            ultima_loja = session.query(Loja).order_by(Loja.created_at.desc()).first()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Lojas", total_lojas)
        with col2:
            st.metric("Lojas Ativas", lojas_ativas)
        with col3:
            st.metric("Lojas Inativas", lojas_inativas)
        with col4:
            if ultima_loja:
                st.metric("Última Loja Criada", ultima_loja.nome)

        style_metric_cards(
            background_color="#008000",
            border_left_color="#FFFFFF",
            border_color="#000000",
            box_shadow="#FFFFFF"
        )

        fig = px.bar(x=["Ativas", "Inativas"], y=[lojas_ativas, lojas_inativas],
                     title="Status das Lojas", labels={"x": "Status", "y": "Quantidade"})
        st.plotly_chart(fig, use_container_width=True)


# Função para carregar dados do banco de dados
def load_data(session):
    # Consulta principal: Produtos com join nas tabelas relacionadas
    query = """
    SELECT 
        p.id AS produto_id,
        p.nome AS produto_nome,
        p.descricao AS produto_descricao,
        p.preco AS produto_preco,
        p.estoque AS produto_estoque,
        p.imagem AS produto_imagem,
        p.status AS produto_status,
        p.link AS produto_link,
        l.id AS loja_id,
        l.nome AS loja_nome,
        l.cnpj AS loja_cnpj,
        l.telefone AS loja_telefone,
        l.email AS loja_email,
        c.nome AS categoria_nome
    FROM oraculo_loja l
    LEFT JOIN oraculo_produto p ON p.loja_id = l.id
    LEFT JOIN categoria_produto c ON p.categoria_id = c.id
    WHERE l.status = 1
    ORDER BY 
        CASE WHEN p.created_at IS NOT NULL THEN 0 ELSE 1 END, -- Prioriza produtos com created_at não nulo
        p.created_at DESC, -- Ordena por data de criação (descendente)
        l.nome ASC -- Ordena por nome da loja (ascendente)
    """
    result = session.execute(text(query)).fetchall()
    return result


def show_loja():
    st.header("🛍️ Produtos Disponíveis")

    # Carregar dados do banco de dados
    with Session() as session:
        produtos_lojas = load_data(session)

    # Barra de Pesquisa por Loja ou Produto (3 letras iniciais ou ID da loja)
    search_query = st.text_input("🔍 Pesquisar por Loja ou Produto (3 letras iniciais ou ID da loja)")
    filtered_data = []

    if search_query:
        # Verificar se o input é um número (pesquisa por ID da loja)
        if search_query.isdigit() and len(search_query) >= 0:
            try:
                # Converter o ID da loja para inteiro para comparação segura
                search_id = int(search_query)
                filtered_data = [row for row in produtos_lojas if row.loja_id == search_id]
            except ValueError:
                st.warning("⚠️ ID da loja inválido. Por favor, insira um número válido.")
        else:
            # Pesquisa por nome da loja ou produto (ignorando maiúsculas/minúsculas)
            filtered_data = [
                row for row in produtos_lojas
                if (row.loja_nome and search_query.lower() in row.loja_nome.lower()) or
                   (row.produto_nome and search_query.lower() in row.produto_nome.lower())
            ]

        # Exibir mensagem se nenhum resultado for encontrado
        if not filtered_data:
            st.warning("⚠️ Nenhuma loja encontrada.")
    else:
        # Se não houver pesquisa, exibir todos os produtos
        filtered_data = produtos_lojas

    # Organizar produtos por loja
    lojas = {}
    for row in filtered_data:
        if row.loja_nome not in lojas:
            lojas[row.loja_nome] = {
                "id": row.loja_id,
                "cnpj": row.loja_cnpj,
                "telefone": row.loja_telefone,
                "email": row.loja_email,
                "produtos": []
            }
        lojas[row.loja_nome]["produtos"].append({
            "id": row.produto_id,
            "nome": row.produto_nome,
            "descricao": row.produto_descricao,
            "preco": row.produto_preco,
            "estoque": row.produto_estoque,
            "imagem": row.produto_imagem,
            "link": row.produto_link,
            "categoria": row.categoria_nome
        })

    # Exibir cada loja e seus produtos
    for loja_nome, loja_info in lojas.items():
        with st.expander(f"🏪 **{loja_nome}** (ID: {loja_info['id']})"):
            st.write(
                f"📞 Telefone: {loja_info['telefone']} | 📧 Email: {loja_info['email']} | 🏢 CNPJ: {loja_info['cnpj']}")

            # Barra de Pesquisa Inteligente dentro da loja (por categoria ou nome do produto)
            search_loja = st.text_input(f"🔍 Pesquisar na loja '{loja_nome}' por Categoria ou Nome do Produto")
            produtos_filtrados = [
                produto for produto in loja_info["produtos"]
                if search_loja.lower() in produto["categoria"].lower() or search_loja.lower() in produto["nome"].lower()
            ] if search_loja else loja_info["produtos"]

            # Exibir produtos em 3 colunas com bordas
            cols = st.columns(
                3,  # Número de colunas
                gap="small",  # Espaçamento pequeno entre as colunas
                vertical_alignment="center",  # Alinhamento vertical no topo

            )
            for i, produto in enumerate(produtos_filtrados):
                with cols[i % 3]:
                    # Adicionar borda ao container usando CSS personalizado
                    st.markdown(
                        f"""
                        <style>
                            .produto-container {{
                                border: 2px solid #ddd;
                                border-radius: 10px;
                                padding: 15px;
                                margin-bottom: 15px;
                                background-color: #f9f9f9;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }}
                            .produto-container h3 {{
                                color: #333; /* Cor do título */
                                font-size: 18px;
                                margin-bottom: 10px;
                            }}
                            .produto-container p {{
                                color: #555; /* Cor da descrição */
                                font-size: 14px;
                                margin-bottom: 5px;
                            }}
                            .produto-container a {{
                                color: #007BFF; /* Cor do link */
                                text-decoration: none;
                                font-weight: bold;
                            }}
                        </style>
                        <div class="produto-container">
                        """,
                        unsafe_allow_html=True
                    )
                    # Imagem
                    st.image(produto["imagem"], caption=produto["nome"], width=200)

                    # Título do produto
                    st.markdown(f"**{produto['nome']}**")

                    # Descrição
                    st.write(produto["descricao"])

                    # Preço e Estoque
                    st.write(f"💰 R$ {produto['preco']:.2f}")
                    st.write(f"📦 Estoque: {produto['estoque']}")

                    # Link de compra
                    st.markdown(f"[🔗 Comprar]({produto['link']})", unsafe_allow_html=True)