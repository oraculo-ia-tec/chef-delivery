import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from sqlalchemy import (create_engine, Column, BigInteger, String, Text, DECIMAL, Integer, Boolean, DateTime,
                        ForeignKey, text, func)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from key_config import DATABASE_URL
import re
import replicate



# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class CategoriaProduto(Base):
    __tablename__ = "categoria_produto"  # Nome da tabela no banco de dados
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)  # Garante que o nome seja único
    descricao = Column(String(255), nullable=True)

    # Relacionamento com Produto
    produtos = relationship("Produto", back_populates="categoria")


class Produto(Base):
    __tablename__ = "oraculo_produto"  # Nome da tabela no banco de dados
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    preco = Column(DECIMAL(10, 2), nullable=False)
    estoque = Column(Integer, default=0)
    imagem = Column(String(255), nullable=True)
    status = Column(Boolean, default=True)
    categoria_id = Column(BigInteger, ForeignKey('categoria_produto.id'), nullable=False)  # Relacionamento com CategoriaProduto
    loja_id = Column(BigInteger, nullable=False)  # Adicionado o campo loja_id
    link = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamento com CategoriaProduto
    categoria = relationship("CategoriaProduto", back_populates="produtos")


# Função para obter dados dos produtos
def obter_dados_produtos():
    with engine.connect() as connection:
        query = "SELECT * FROM oraculo_produto"  # Ajuste conforme necessário
        return pd.read_sql(query, connection)


def salvar_categoria(nome, descricao=None):
    try:
        with Session() as session:
            # Verifica se a categoria já existe
            categoria_existente = session.query(CategoriaProduto).filter_by(nome=nome).first()
            if categoria_existente:
                st.error(f"A categoria '{nome}' já existe.")
                return False

            nova_categoria = CategoriaProduto(
                nome=nome,
                descricao=descricao
            )
            session.add(nova_categoria)
            session.commit()
            return True  # Retorna True se a inserção for bem-sucedida
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao salvar categoria: {e}")
        return False


def salvar_produto(nome, descricao, preco, estoque, imagem, status, categoria_id, link, loja_id):
    try:
        with Session() as session:
            novo_produto = Produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                estoque=estoque,
                imagem=imagem,
                status=status,
                categoria_id=categoria_id,
                link=link,
                loja_id=loja_id  # Passando o ID da lojas
            )
            session.add(novo_produto)
            session.commit()
            return True  # Retorna True se a inserção for bem-sucedida
    except Exception as e:
        session.rollback()
        print(f"Erro ao salvar produto: {e}")
        return False  # Retorna False em caso de erro


def selecionar_loja():
    """Busca todas as lojas cadastradas e permite ao usuário selecionar pelo nome."""
    with Session() as session:
        lojas = session.execute(text("SELECT id, nome FROM oraculo_loja")).fetchall()

    if not lojas:
        st.warning("⚠️ Nenhuma lojas cadastrada. Cadastre uma lojas antes de adicionar produtos.")
        return None

    # Criar um dicionário {Nome da Loja: ID}
    lojas_dict = {loja[1]: loja[0] for loja in lojas}

    # Criar um selectbox para o usuário escolher a lojas pelo nome
    loja_selecionada = st.selectbox("Selecione a Loja", list(lojas_dict.keys()))

    return lojas_dict[loja_selecionada]  # Retorna o ID da lojas escolhida


# 🔹 Função para obter categorias da lojas
def obter_nome_categoria():
    """Obtém categorias de lojas e retorna uma lista de nomes."""
    with engine.connect() as connection:
        query = text("SELECT nome FROM categoria_produto")
        result = connection.execute(query).fetchall()
        return [row[0] for row in result]  # Retorna uma lista com os nomes das categorias


def obter_produtos_por_categoria():
    """Obtém produtos do banco de dados e retorna um dicionário {Categoria: [Produtos]}."""
    produtos_categoria = {}
    with engine.connect() as connection:
        query = text("""
            SELECT p.nome, p.descricao, p.preco, p.link, p.imagem, c.nome AS categoria 
            FROM oraculo_produto p 
            JOIN categoria_produto c ON p.categoria_id = c.id
        """)
        result = connection.execute(query)
        rows = result.fetchall()

        # Obter os nomes das colunas e convertê-los para uma lista
        colunas = list(result.keys())

        for row in rows:
            # Transformar a linha em um dicionário
            produto = {
                "nome": row[colunas.index("nome")],
                "descricao": row[colunas.index("descricao")],
                "preco": row[colunas.index("preco")],
                "link": row[colunas.index("link")],
                "imagem": row[colunas.index("imagem")]
            }
            categoria = row[colunas.index("categoria")]

            if categoria not in produtos_categoria:
                produtos_categoria[categoria] = []
            produtos_categoria[categoria].append(produto)

    return produtos_categoria


# Função para listar produtos cadastrados
def listar_produtos():
    with Session() as session:
        produtos = session.query(Produto).all()
        for produto in produtos:
            produto.preco = float(produto.preco)  # Converte Decimal para float
        return produtos


# Função para atualizar um produto existente
def atualizar_produto(produto_id, dados_atualizados):
    with Session() as session:
        produto = session.get(Produto, produto_id)
        if not produto:
            st.error("⚠️ Produto não encontrado.")
            return False  # Retorna False se o produto não existir

        for key, value in dados_atualizados.items():
            setattr(produto, key, value)
        session.commit()
        return True  # Retorna True se a atualização for bem-sucedida


# Função para deletar um produto
def deletar_produto(categoria, produto_nome):
    """Remove um produto da categoria selecionada e atualiza a planilha."""
    try:
        if categoria not in st.session_state.categorias:
            st.error("⚠️ Categoria não encontrada.")
            return False

        produtos = st.session_state.categorias[categoria]
        produto_removido = next((p for p in produtos if p["nome"] == produto_nome), None)

        if not produto_removido:
            st.warning("⚠️ Produto não encontrado na categoria.")
            return False

        produtos.remove(produto_removido)  # Remove o produto da lista

        # Verifica se há imagem associada e a remove do diretório
        if "imagem" in produto_removido and produto_removido["imagem"]:
            if os.path.exists(produto_removido["imagem"]):
                os.remove(produto_removido["imagem"])

        salvar_dados_em_excel()  # Atualiza o Excel após remoção
        st.success(f"✅ Produto '{produto_nome}' removido com sucesso!")
        return True
    except Exception as e:
        st.error(f"🚨 Erro ao deletar o produto: {e}")
        return False


# Diretório de imagens dos produtos
IMAGE_DIR = "./media/src/img/produto"
EXCEL_FILE = "produtos.xlsx"


# Criar diretório se não existir
os.makedirs(IMAGE_DIR, exist_ok=True)


# Criar arquivo Excel se não existir
if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=["Categoria", "Nome", "Preço", "Descrição", "Link", "Imagem"]).to_excel(
        EXCEL_FILE, index=False, sheet_name="Produtos", engine="openpyxl"
    )


# 🔹 Função para salvar dados no Excel
def salvar_dados_em_excel():
    with Session() as session:
        produtos_data = []
        result = session.execute(text("SELECT categoria_id, nome, preco, descricao, link, imagem FROM oraculo_produto"))
        rows = result.fetchall()

        # Obter os nomes das colunas e convertê-los para uma lista
        colunas = list(result.keys())

        for row in rows:
            produtos_data.append({
                "Categoria": row[colunas.index("categoria_id")],
                "Nome": row[colunas.index("nome")],
                "Preço": row[colunas.index("preco")],
                "Descrição": row[colunas.index("descricao")],
                "Link": row[colunas.index("link")],
                "Imagem": row[colunas.index("imagem")]
            })

    df_produtos = pd.DataFrame(produtos_data)
    df_produtos.to_excel(EXCEL_FILE, index=False, sheet_name="Produtos", engine="openpyxl")


# 🔹 Função para deletar produto
def deletar_produto(categoria, produto_nome):
    """Remove um produto da categoria selecionada e atualiza a planilha."""
    try:
        if categoria in st.session_state.categorias:
            produtos = st.session_state.categorias[categoria]
            produto_removido = next((p for p in produtos if p["nome"] == produto_nome), None)

            if produto_removido:
                produtos.remove(produto_removido)  # Remove o produto da lista

                # Verifica se há imagem associada e a remove do diretório
                if "imagem" in produto_removido and produto_removido["imagem"]:
                    if os.path.exists(produto_removido["imagem"]):
                        os.remove(produto_removido["imagem"])

                salvar_dados_em_excel()  # Atualiza o Excel após remoção
                st.success(f"✅ Produto '{produto_nome}' removido com sucesso!")
            else:
                st.warning("⚠️ Produto não encontrado na categoria.")
        else:
            st.error("⚠️ Categoria não encontrada.")
    except Exception as e:
        st.error(f"🚨 Erro ao deletar o produto: {e}")


# Função para obter o caminho completo da imagem do usuário
def get_image_produto(product_image):
    """
    Retorna o caminho completo da imagem do produto.
    Se a imagem não existir, retorna um caminho padrão.
    """
    if user_image:
        image_path = os.path.join("./media/src/img/produto", product_image)
        if os.path.exists(image_path):
            return image_path


def cadastrar_produto():

    # Inicializa categorias e produtos no estado da sessão
    if "categorias" not in st.session_state:
        st.session_state.categorias = {}

    if "produtos" not in st.session_state:
        st.session_state.produtos = {}

    # 📦 **Interface Principal**
    st.title("📦 Gerenciamento de Produtos")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Cadastrar", "📦 Listar Produtos",
        "✏️ Editar/Excluir",
        "📊 Estatísticas de Preços",
        "📈 Análise Inteligente"
    ])

    # 📝 **Aba de Cadastro**
    with tab1:
        st.header("Cadastrar Categoria e Produto")

        # 🔹 Cadastro de Categorias
        with st.expander("📂 Adicionar Categoria"):
            with st.form("form_cadastro_categoria", clear_on_submit=True, border=True):
                categoria_nome = st.text_input("Digite o nome da nova categoria:")
                descricao_categoria = st.text_input("Digite uma descrição (opcional): ")
                if st.form_submit_button("✅ Cadastrar Categoria"):
                    if categoria_nome.strip():
                        sucesso = salvar_categoria(categoria_nome, descricao_categoria)
                        if sucesso:
                            st.success(f"Categoria '{categoria_nome}' cadastrada!")
                        else:
                            st.error("⚠️ Falha ao cadastrar a categoria no banco de dados.")
                    else:
                        st.error("⚠️ Nome inválido ou vazio.")

        # 🔹 Cadastro de Produtos
        with st.expander("📝 Adicionar Produto"):
            with st.form("form_cadastro_produto", clear_on_submit=True, border=True):
                categorias = obter_nome_categoria()

                if not categorias:
                    st.warning("Cadastre pelo menos uma categoria primeiro.")
                else:
                    categoria_nome = st.selectbox("Escolha a Categoria", categorias)
                    loja_id = selecionar_loja()  # Obtém o ID da lojas escolhida pelo usuário
                    nome = st.text_input("Nome do Produto")
                    descricao = st.text_area("Descrição")
                    preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f")
                    estoque = st.number_input("Quantidade em Estoque", min_value=0, step=1)
                    link = st.text_input("Link do Produto")
                    imagem = st.file_uploader("Imagem do Produto", type=["jpg", "jpeg", "png"])

                    # Botão de envio do formulário
                    submitted = st.form_submit_button("✅ Cadastrar Produto")
                    if submitted:
                        if nome.strip() and preco > 0 and descricao.strip() and link.strip():
                            try:
                                image_path = ""
                                if imagem:
                                    nome_arquivo = f"{nome.replace(' ', '_')}.jpg"
                                    image_path = os.path.join(IMAGE_DIR, nome_arquivo)
                                    with open(image_path, "wb") as f:
                                        f.write(imagem.getbuffer())

                                # Verifica se a categoria existe
                                with Session() as session:
                                    categoria = session.query(CategoriaProduto).filter_by(nome=categoria_nome).first()
                                    if not categoria:
                                        st.error(f"⚠️ A categoria '{categoria_nome}' não foi encontrada.")
                                        return

                                # Salvar produto no banco de dados
                                sucesso = salvar_produto(
                                    nome=nome,
                                    descricao=descricao,
                                    preco=preco,
                                    estoque=estoque,
                                    imagem=image_path if imagem else "",
                                    status=True,
                                    categoria_id=categoria.id,  # Usa o ID da categoria
                                    link=link,
                                    loja_id=loja_id
                                )

                                if sucesso:
                                    st.success(f"🎉 Produto {nome} cadastrado com sucesso!")
                                    st.balloons()
                                else:
                                    st.error("⚠️ Falha ao salvar o produto no banco de dados.")
                            except Exception as e:
                                st.error(f"Erro durante o cadastro: {e}")
                        else:
                            st.error("⚠️ Preencha todos os campos corretamente.")

    # 📦 **Aba de Listagem de Produtos**
    with tab2:
        st.subheader("📋 Visualizar produtos cadastrados")
        produtos_cadastrados = False  # Variável para verificar se há produtos

        produtos_por_categoria = obter_produtos_por_categoria()  # Obtém os produtos do banco de dados

        for categoria, produtos in produtos_por_categoria.items():
            if produtos:
                produtos_cadastrados = True  # Marcar que existem produtos cadastrados
                with st.expander(f"📌 Categoria: {categoria}"):
                    for produto in produtos:
                        col1, col2 = st.columns([1, 3])

                        with col1:
                            if produto["imagem"] and os.path.exists(produto["imagem"]):
                                st.image(produto["imagem"], width=150)
                            else:
                                st.write("❌ Sem imagem disponível")

                        with col2:
                            st.subheader(f"🔹 {produto['nome']}")
                            st.write(f"💬 {produto['descricao']}")
                            st.write(f"💰 **Preço:** R$ {produto['preco']:.2f}")
                            if produto["link"]:
                                st.markdown(f"[🛒 Comprar Agora]({produto['link']})", unsafe_allow_html=True)
                        st.divider()

        # Exibir mensagem se não houver produtos
        if not produtos_cadastrados:
            st.info("Ainda não foi cadastrado nenhum produto.")

    # ✏️ **Aba de Edição/Exclusão**
    with tab3:
        st.header("✏️ Editar ou Excluir Produtos")

        # Verifica se há produtos cadastrados no banco de dados
        with Session() as session:
            produtos = session.query(Produto).all()

        if not produtos:
            st.warning("⚠️ Nenhum produto cadastrado.")
        else:
            # Lista de nomes dos produtos para seleção
            produtos_nomes = [produto.nome for produto in produtos]
            produto_selecionado = st.selectbox("Escolha o produto:", produtos_nomes, key="produto_editar")

            # Busca o produto selecionado no banco de dados
            produto_atual = next((p for p in produtos if p.nome == produto_selecionado), None)

            if produto_atual:
                # Criando campos de edição
                novo_nome = st.text_input("Nome do Produto", produto_atual.nome, key="novo_nome")
                novo_preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f",
                                             value=float(produto_atual.preco), key="novo_preco")
                nova_descricao = st.text_area("Descrição", produto_atual.descricao, key="nova_descricao")
                novo_link = st.text_input("Link de Pagamento", produto_atual.link, key="novo_link")
                nova_imagem = st.file_uploader("📸 Atualizar Imagem", type=["jpg", "jpeg", "png"], key="nova_imagem")

                # Botão para salvar alterações
                if st.button("💾 Salvar Alterações"):
                    try:
                        # Atualizar imagem, se uma nova for enviada
                        image_path = produto_atual.imagem
                        if nova_imagem:
                            nome_arquivo = f"{novo_nome.replace(' ', '_')}.jpg"
                            image_path = os.path.join(IMAGE_DIR, nome_arquivo)
                            with open(image_path, "wb") as f:
                                f.write(nova_imagem.getbuffer())

                            # Remove a imagem antiga, se existir
                            if produto_atual.imagem and os.path.exists(produto_atual.imagem):
                                os.remove(produto_atual.imagem)

                        # Atualizar dados no banco de dados
                        dados_atualizados = {
                            "nome": novo_nome,
                            "preco": novo_preco,
                            "descricao": nova_descricao,
                            "link": novo_link,
                            "imagem": image_path
                        }
                        sucesso = atualizar_produto(produto_atual.id, dados_atualizados)

                        if sucesso:
                            st.success("✅ Produto atualizado com sucesso!")
                        else:
                            st.error("⚠️ Falha ao atualizar o produto.")
                    except Exception as e:
                        st.error(f"🚨 Erro ao salvar alterações: {e}")

                # Botão para excluir o produto
                if st.button("❌ Excluir Produto"):
                    try:
                        sucesso = deletar_produto(produto_atual.id)
                        if sucesso:
                            st.success("✅ Produto excluído com sucesso!")
                        else:
                            st.error("⚠️ Falha ao excluir o produto.")
                    except Exception as e:
                        st.error(f"🚨 Erro ao excluir o produto: {e}")
            else:
                st.warning("⚠️ Produto não encontrado.")

    # 📊 **Estatísticas de Produtos**
    with tab4:
        st.header("📊 Estatísticas de Produtos")

        # Consultar métricas diretamente do banco de dados
        with Session() as session:
            # Total de produtos cadastrados
            total_produtos = session.query(func.count(Produto.id)).scalar()

            # Total de categorias únicas
            total_categorias = session.query(func.count(func.distinct(Produto.categoria_id))).scalar()

            # Consultar dados de produtos para calcular o total em estoque
            produtos = session.query(Produto.preco, Produto.estoque).all()

            # Cálculo do total em estoque
            total_estoque_valor = sum(preco * estoque for preco, estoque in produtos)

            # Cálculo do preço médio
            preco_medio = session.query(func.avg(Produto.preco)).scalar()
            preco_medio = float(preco_medio) if preco_medio is not None else "N/A"  # Converte Decimal para float

            # Garantir que o total em estoque não seja None
            total_estoque_valor = total_estoque_valor if total_estoque_valor is not None else 0

            # Distribuição de produtos por categoria
            distribuicao_categorias = session.query(
                CategoriaProduto.nome,
                func.count(Produto.id)
            ).join(Produto, Produto.categoria_id == CategoriaProduto.id).group_by(CategoriaProduto.nome).all()

        # Exibir métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="📦 Total de Produtos", value=total_produtos if total_produtos else 0)

        with col2:
            st.metric(label="📁 Total de Categorias", value=total_categorias if total_categorias else 0)

        with col3:
            st.metric(label="💰 Total em Estoque (R$)", value=f"{total_estoque_valor:.2f}")

        with col4:
            st.metric(label="💰 Preço Médio (R$)",
                      value=f"{preco_medio:.2f}" if isinstance(preco_medio, float) else "N/A")

        st.divider()

        # Gráficos
        if distribuicao_categorias:
            # Transformar os dados em um DataFrame para facilitar a criação dos gráficos
            df_distribuicao = pd.DataFrame(distribuicao_categorias, columns=["Categoria", "Quantidade"])

            # Gráfico de Barras
            fig_bar = px.bar(
                df_distribuicao,
                x="Categoria",
                y="Quantidade",
                title="Distribuição de Produtos por Categoria",
                color="Categoria",
                text_auto=True
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Gráfico de Pizza
            fig_pizza = px.pie(
                df_distribuicao,
                names="Categoria",
                values="Quantidade",
                title="Proporção de Produtos por Categoria"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para gerar os gráficos.")

    # 📈 **Aba de Análise Inteligente**
    with tab5:
        st.header("📈 Análise Inteligente")
        st.subheader("📖 Narrativa Gerada Automaticamente")

        # Consultar dados do banco de dados
        with Session() as session:
            # Consulta para obter produtos e suas categorias
            produtos = session.execute(text("""
                SELECT p.nome AS produto_nome, p.preco, p.estoque, c.nome AS categoria_nome, l.nome AS loja_nome
                FROM oraculo_produto p
                JOIN categoria_produto c ON p.categoria_id = c.id
                JOIN oraculo_loja l ON p.loja_id = l.id
            """)).fetchall()

            # Consulta para obter estatísticas agregadas
            total_produtos = session.query(func.count(Produto.id)).scalar()
            preco_medio = session.query(func.avg(Produto.preco)).scalar()
            estoque_total = session.query(func.sum(Produto.estoque)).scalar()

        # Estruturar os dados para análise
        dados_analise = {
            "total_produtos": total_produtos,
            "preco_medio": float(preco_medio) if preco_medio else 0,
            "estoque_total": estoque_total if estoque_total else 0,
            "produtos": [
                {
                    "produto_nome": row.produto_nome,
                    "preco": float(row.preco),
                    "estoque": row.estoque,
                    "categoria_nome": row.categoria_nome,
                    "loja_nome": row.loja_nome
                }
                for row in produtos
            ]
        }

        # Formatar os dados para entrada no modelo
        system_prompt = f"""
        Com base nos dados fornecidos, gere uma narrativa inteligente sobre o desempenho dos produtos:
        - Total de Produtos: {dados_analise['total_produtos']}
        - Preço Médio: R$ {dados_analise['preco_medio']:.2f}
        - Estoque Total: {dados_analise['estoque_total']}
        - Detalhes dos Produtos:
        """

        # Set a default model
        if "deepseek_model" not in st.session_state:
            st.session_state["deepseek_model"] = "deepseek-ai/deepseek-r1"

        # Interface do chat
        if "massages_pro" not in st.session_state:
            st.session_state.massages_pro = []

        # Contêiner para o histórico de mensagens
        chat_container = st.container()

        # Exibir histórico de mensagens dentro do contêiner
        with chat_container:
            for message in st.session_state.massages_pro:
                with st.chat_message(message["role"], avatar=get_user_image_path(message.get("avatar"))):
                    st.markdown(message["content"])

        # Campo de entrada fixo na parte inferior
        prompt = st.chat_input("Pergunte sobre lojas e produtos.", key="chat_input")

        def clear_chat_history():
            st.session_state.massages_pro = [{
                "role": "assistant", "content": 'Olá! Sou o MESTRE BÍBLIA, pronto para ajudá-lo a compreender as '
                                                'análises sobre lojas e produtos.'}]

        st.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

        # Processar nova mensagem
        if prompt:
            # Adicionar mensagem do usuário
            st.session_state.massages_pro.append(
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
                        st.session_state.massages_pro.append({"role": "assistant", "content": clean_response})

                    except Exception as e:
                        st.error(f"Erro ao gerar análise: {str(e)}")


    # Aplicar estilo aos cards 📌
    style_metric_cards(
        background_color="#008000",  # verde
        border_left_color="#FFFFFF",
        border_color="#000000",
        box_shadow="#FFFFFF"
    )

if __name__ == "__main__":
    st.set_page_config(page_title="Cadastrar Produtos", page_icon="📦", layout="wide")
    cadastrar_produto()  # Chama a função que será responsável pela lógica de cadastro de produtos