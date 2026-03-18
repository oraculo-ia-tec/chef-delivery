import streamlit as st
# ...existing code...
            headers={'access_token': ''}
        )
        response.raise_for_status()
        return response.json()


async def showCliente():

    st.title("Sistema Flash Pagamentos")
    st.header("Criar Novo Cliente")

    # Formulário para cadastro de cliente
    with st.form(key='form_cliente'):
        # Cria colunas para organizar os campos
        col1, col2 = st.columns(2)  # Colunas para Nome e WhatsApp/Email
        col3, col4 = st.columns(2)  # Colunas para Endereço e Bairro/CEP

        # Coleta de dados do cliente
        with col1:
            nome = st.text_input("Nome")  # Nome em uma coluna
            documento = st.text_input("CPF/CNPJ")
        with col2:
            email = st.text_input("E-mail")  # E-mail e WhatsApp em uma coluna
            whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111')

        with col3:
            endereco = st.text_input("Endereço")  # Endereço em uma coluna
            bairro = st.text_input("Bairro")
        with col4:
              # Bairro e CEP em uma coluna
            cep = st.text_input("CEP")
            city = st.text_input("Cidade:")

        # Botão para enviar os dados do formulário
        submit_button = st.form_submit_button("ENVIAR!")

        if submit_button:
            cliente = Cliente(
                nome=nome,
                email=email,
                cpf_cnpj=documento,
                whatsapp=whatsapp,
                endereco=endereco,
                cep=cep,
                bairro=bairro,
                cidade=city
            )
            loop = asyncio.get_event_loop()
            try:
                resultado = loop.run_until_complete(create_customer(cliente))
                st.success(f"Cliente {resultado['nome']} criado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao criar cliente: {e}")



