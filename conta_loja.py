import streamlit as st
from sqlalchemy.orm import Session


# Inicializa o session state
if "cargo" not in st.session_state:
    st.session_state.cargo = ''

if "produtos" not in st.session_state:
    st.session_state.produtos = []

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []


def comprar_produto():
    if len(st.session_state.produtos) > 0:
        st.header("Comprar Produto")
        with st.expander("Clique para ver os produtos disponíveis"):
            for produto in st.session_state.produtos:
                st.write(
                    f"Código: {produto._Produto__codigo}, Nome: {produto._Produto__nome}, Preço: {produto._Produto__preco}")

            codigo = st.number_input("Informe o código do produto que deseja adicionar ao carrinho:", min_value=1,
                                     step=1)

            if st.button("Adicionar ao Carrinho"):
                produto = pega_produto_por_codigo(codigo)

                if produto:
                    if len(st.session_state.carrinho) > 0:
                        tem_no_carrinho = False
                        for item in st.session_state.carrinho:
                            quant = item.get(produto)
                            if quant:
                                item[produto] = quant + 1
                                st.success(
                                    f'O produto {produto._Produto__nome} agora possui {quant + 1} unidades no carrinho.')
                                tem_no_carrinho = True
                                break
                        if not tem_no_carrinho:
                            st.session_state.carrinho.append({produto: 1})
                            st.success(f'O produto {produto._Produto__nome} foi adicionado ao carrinho.')
                    else:
                        st.session_state.carrinho.append({produto: 1})
                        st.success(f'O produto {produto._Produto__nome} foi adicionado ao carrinho.')
                else:
                    st.error(f'O produto com código {codigo} não foi encontrado.')
    else:
        st.warning("Ainda não existem produtos para vender.")


# Chame a função para comprar o produto
comprar_produto()


def buscar_compras_por_usuario(usuario_id: int, db: Session) -> list:
    # Consulta a tabela de compras filtrando pelo ID do usuário
    compras = db.query(Compra).filter(Compra.usuario_id == usuario_id).all()
    # Transformar as compras em um formato de dicionário para facilitar a exibição
    return [{"produto": compra.produto.nome, "quantidade": compra.quantidade, "preco": compra.produto.preco} for compra in compras]


def buscar_compras_por_tipo_usuario(tipo_usuario: str, db: Session) -> list:
    # Exemplo de lógica para filtrar compras com base no tipo de usuário
    if tipo_usuario == "admin":
        # Um administrador pode ver todas as compras
        compras = db.query(Compra).all()
    else:
        # Para outros tipos de usuários, você pode definir condições específicas
        compras = db.query(Compra).filter(Compra.tipo_usuario == tipo_usuario).all()

    # Transformar as compras em um formato de dicionário para facilitar a exibição
    return [{"produto": compra.produto.nome, "quantidade": compra.quantidade, "preco": compra.produto.preco} for compra
            in compras]


def formata_float_str_moeda(valor: float) -> str:
    return f'R$ {valor:.2f}'

def pega_produto_por_codigo(codigo: int) -> None:
    for produto in st.session_state.produtos:
        if produto.codigo == codigo:
            return produto
    return None

def visualizar_carrinho():
    if st.session_state.carrinho:
        st.header("Produtos no Carrinho")
        for item in st.session_state.carrinho:
            for produto, quantidade in item.items():
                st.write(f"Produto: {produto.nome}, Quantidade: {quantidade}, Preço Unitário: {formata_float_str_moeda(produto.preco)}")
                st.write("---------------")
    else:
        st.warning("Ainda não existem produtos no carrinho.")

def fechar_pedido():
    if st.session_state.carrinho:
        valor_total = 0
        st.header("Produtos do Carrinho")
        for item in st.session_state.carrinho:
            for produto, quantidade in item.items():
                st.write(f"Produto: {produto.nome}, Quantidade: {quantidade}, Preço Unitário: {formata_float_str_moeda(produto.preco)}")
                valor_total += produto.preco * quantidade
                st.write("---------------")
        st.write(f"Sua fatura é: {formata_float_str_moeda(valor_total)}")
        st.success("Obrigado pela sua compra! Volte sempre!")
        st.session_state.carrinho.clear()
    else:
        st.warning("Ainda não existem produtos no carrinho para fechar o pedido.")

def pagina_compras():
    st.header("Minhas Compras")
    tipo_usuario = st.session_state.role

    if tipo_usuario in ["admin", "Pastor", "Lider", "colaborador", "membro"]:
        st.write(f"Como {tipo_usuario}, você pode ver suas compras.")
        exibir_compras(tipo_usuario)
    elif tipo_usuario == "cliente":
        st.write("Aqui estão os produtos que você comprou:")
        exibir_compras_usuario(st.session_state.usuario_id)
    else:
        st.warning("Tipo de usuário não reconhecido.")

def exibir_compras(tipo_usuario):
    # Lógica para buscar e exibir as compras do tipo de usuário
    # Aqui deve ser implementada a lógica que acessa o banco de dados ou sistema de armazenamento para recuperar as compras
    compras = buscar_compras_por_tipo_usuario(tipo_usuario)
    for compra in compras:
        st.write(f"Produto: {compra['produto']}, Quantidade: {compra['quantidade']}, Preço: {formata_float_str_moeda(compra['preco'])}")

    st.warning("Lógica de exibição de compras deve ser implementada aqui.")

def exibir_compras_usuario(usuario_id):
    # Lógica para buscar e exibir apenas as compras do usuário autenticado
    compras = buscar_compras_por_usuario(usuario_id)
    for compra in compras:
        st.write(f"Produto: {compra['produto']}, Quantidade: {compra['quantidade']}, Preço: {formata_float_str_moeda(compra['preco'])}")

    st.warning("Lógica de exibição de compras do usuário deve ser implementada aqui.")


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


def showConta():
    st.markdown("<h1 style='text-align: center;'>🛒Store Recomeçar</h1>", unsafe_allow_html=True)

    if st.session_state.produtos:
        with st.expander("Comprar Produto"):
            for produto in st.session_state.produtos:
                st.write(f"Código: {produto.codigo}, Nome: {produto.nome}, Preço: {formata_float_str_moeda(produto.preco)}")

            codigo = st.number_input("Informe o código do produto que deseja adicionar ao carrinho:", min_value=1, step=1)

            if st.button("Adicionar ao Carrinho"):
                produto = pega_produto_por_codigo(codigo)

                if produto:
                    for item in st.session_state.carrinho:
                        if produto in item:
                            item[produto] += 1
                            st.success(f'O produto {produto.nome} agora possui {item[produto]} unidades no carrinho.')
                            break
                    else:
                        st.session_state.carrinho.append({produto: 1})
                        st.success(f'O produto {produto.nome} foi adicionado ao carrinho.')
                else:
                    st.error(f'O produto com código {codigo} não foi encontrado.')
    else:
        st.warning("Ainda não existem produtos para vender.")

    with st.expander("Visualizar Carrinho"):
        visualizar_carrinho()

    with st.expander("Fechar Pedido"):
        fechar_pedido()

    with st.expander("Minhas Compras"):
        pagina_compras()