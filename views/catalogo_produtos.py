import streamlit as st
import pandas as pd
from produtos import ProdutoCatalogo, Categoria
from PIL import Image
import os


# Inicialização do session state para categorias
if 'categorias' not in st.session_state:
    st.session_state.categorias = None


def pega_produto_por_codigo(codigo: int) -> ProdutoCatalogo:
    for produto in st.session_state.produtos:
        if produto.codigo == codigo:
            return produto
    return None


# Função para salvar dados em um arquivo Excel
def salvar_dados_em_excel(categorias):
    produtos_data = []
    for categorias, categoria in categorias.items():
        for produto in categoria.listar_produtos():
            produtos_data.append({
                'Nome da Categoria': categoria,
                'Nome do Produto': produto.nome,
                'Preço': produto.preco,
                'Descrição': produto.descricao,
                'Link de Pagamento': produto.link,
                'Imagem': produto.imagem
            })

    df = pd.DataFrame(produtos_data)
    # Verifica se o arquivo já existe
    if os.path.exists('produtos.xlsx'):
        # Se o arquivo já existir, adiciona os novos dados
        with pd.ExcelWriter('produtos.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet2'].max_row)
    else:
        # Se não existir, cria um novo arquivo
        df.to_excel('produtos.xlsx', index=False)


def cadastrar_listar_comprar():


    if 'produtos' not in st.session_state:
        st.session_state.produtos = []
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    # Formulário para cadastro de categorias
    with st.form("form_categoria"):
        st.session_state.categorias = st.text_input("Nome da Categoria", value=st.session_state.categorias)
        categoria_submitted = st.form_submit_button("Cadastrar Categoria")

        if categoria_submitted:
            if st.session_state.categorias:
                # Verificar duplicidade ignorando case
                if st.session_state.categorias.lower() not in (cat.lower() for cat in st.session_state.categorias()):
                    st.session_state.categorias[st.session_state.categorias] = Categoria(st.session_state.categorias)
                    st.success(f"Categoria '{st.session_state.categorias}' cadastrada com sucesso!")
                    st.session_state.categorias = ''  # Limpa o campo após o cadastro
                else:
                    st.error("A categoria já está cadastrada.")
            else:
                st.error("O nome da categoria não pode ser vazio.")

    with st.form("form_cadastrar_produto"):
        st.header("Cadastrar Produto")
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço do Produto", min_value=0.0)
        descricao = st.text_area("Descrição do Produto")
        uploaded_file = st.file_uploader("escolha uma imagem de perfil", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            st.session_state.image = uploaded_file  # armazena o arquivo de imagem no session_state

            # salva a imagem com o nome de usuário
            username = st.session_state.username  # certifique-se de que o username está previamente definido
            if username:
                directory = "./src/img/catalogo"
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # salva a imagem no formato desejado
                image_path = os.path.join(directory, f"{username}.png")  # ou .jpg, conforme necessário
                image = Image.open(uploaded_file)  # Corrigido de 'image' para 'Image'
                image.save(image_path)
        link = st.text_input("Link do Produto")

        # Botão para enviar o formulário
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            # Cria um novo objeto Produto
            produto = ProdutoCatalogo(nome, preco, descricao, link)
            st.session_state.produtos.append(produto)
            st.success(f'O produto {produto.nome} foi cadastrado com sucesso!')


    if len(st.session_state.produtos) > 0:
        st.header("Listar Produtos")
        with st.expander("Clique para ver os produtos"):
            produtos_data = [{
                'Código': produto.codigo,  # Acessando diretamente o código
                'Nome': produto.nome,
                'Preço': produto.preco,
                'Descrição': produto.descricao,
                'Imagem': produto.imagem,
                'Link': produto.link
            } for produto in st.session_state.produtos]

            # Exibe o DataFrame com os produtos
            df = pd.DataFrame(produtos_data)
            st.dataframe(df)
    else:
        st.warning("Ainda não existem produtos cadastrados.")


    if len(st.session_state.produtos) > 0:
        st.header("Comprar Produto")
        with st.expander("Clique para ver os produtos disponíveis"):
            for produto in st.session_state.produtos:
                st.write(f"Código: {produto.codigo}, Nome: {produto.nome}, Preço: {produto.preco}")

            codigo = st.number_input("Informe o código do produto que deseja adicionar ao carrinho:", min_value=1, step=1)

            if st.button("Adicionar ao Carrinho"):
                produto = pega_produto_por_codigo(codigo)

                if produto:
                    if len(st.session_state.carrinho) > 0:
                        tem_no_carrinho = False
                        for item in st.session_state.carrinho:
                            if produto in item:
                                item[produto] += 1
                                st.success(f'O produto {produto.nome} agora possui {item[produto]} unidades no carrinho.')
                                tem_no_carrinho = True
                                break
                        if not tem_no_carrinho:
                            st.session_state.carrinho.append({produto: 1})
                            st.success(f'O produto {produto.nome} foi adicionado ao carrinho.')
                    else:
                        st.session_state.carrinho.append({produto: 1})
                        st.success(f'O produto {produto.nome} foi adicionado ao carrinho.')
                else:
                    st.error(f'O produto com código {codigo} não foi encontrado.')
    else:
        st.warning("Ainda não existem produtos para vender.")

