import streamlit as st
import os
from transformers import AutoTokenizer
import base64
from fpdf import FPDF
import pandas as pd
import io

import replicate
from langchain.llms import Replicate

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



# --- Verifica se o token da API está nos segredos ---
if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    # Se a chave não está nos segredos, define um valor padrão ou continua sem o token
    replicate_api = None

# Essa parte será executada se você precisar do token em algum lugar do seu código
if replicate_api is None:
    # Se você quiser fazer algo específico quando não há token, você pode gerenciar isso aqui
    # Por exemplo, configurar uma lógica padrão ou deixar o aplicativo continuar sem mostrar nenhuma mensagem:
    st.warning('Um token de API é necessário para determinados recursos.', icon='⚠️')




################################################# ENVIO DE E-MAIL ####################################################
############################################# PARA CONFIRMAÇÃO DE DADOS ##############################################

# Função para enviar o e-mail
def enviar_email(destinatario, assunto, corpo):
    remetente = "mensagem@flashdigital.tech"  # Insira seu endereço de e-mail
    senha = "sua_senha"  # Insira sua senha de e-mail

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('mail.flashdigital.tech', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        st.success("E-mail enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")

    # Enviando o e-mail ao pressionar o botão de confirmação
    if st.button("DADOS CONFIRMADO"):
        # Obter os dados salvos em st.session_state
        nome = st.session_state.user_data["name"]
        whatsapp = st.session_state.user_data["whatsapp"]
        email = st.session_state.user_data["email"]

        # Construindo o corpo do e-mail
        corpo_email = f"""
        Olá {nome},

        Segue a confirmação dos dados:
        - Nome: {nome}
        - WhatsApp: {whatsapp}
        - E-mail: {email}
        - Agendamento : {dias} e {turnos}

        Obrigado pela confirmação!
        """

        # Enviando o e-mail
        enviar_email(email, "Confirmação de dados", corpo_email)


#######################################################################################################################

def show_chat_med():
    # Carregar apenas a aba "Dados" do arquivo Excel
    df_dados = pd.read_excel('./conhecimento/medicos_dados_e_links.xlsx', sheet_name='Dados')

    # Converter o DataFrame para um arquivo de texto, por exemplo, CSV
    df_dados.to_csv('./conhecimento/medicos_dados_e_links.txt', sep=' ', index=False, header=True)

    # Se preferir usar tabulações como delimitador, substitua sep=' ' por sep='\t'
    # df_dados.to_csv('./conhecimento/CatalogoMed_Sudeste_Dados.txt', sep='\t', index=False, header=True)

    # Especifica o caminho para o arquivo .txt
    caminho_arquivo = './conhecimento/medicos_dados_e_links.txt'

    # Abre o arquivo no modo de leitura ('r')
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        # Lê todo o conteúdo do arquivo e armazena na variável 'conteudo'
        info = arquivo.read()

    # Exibe o conteúdo do arquivo
    df_txt = info

    system_prompt = f'''
    Você é o Doutor Med (DM), você tem formação acadêmica sólida em Farmácia, incluindo Bacharelado, Mestrado em Ciências 
    Farmacêuticas e Doutorado em Farmacologia, você é formado em analista de dados e se especializou em análise de dados médidcos.
    Você fará a leitura e análise dos dados: {df_txt} e dará informações precisas e exatas dos dados, dará respostas com 
    o máximo de precisão como analista de dados. 
    '''

    # Função para gerar o PDF
    def create_pdf(messages):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for message in messages:
            role = message["role"].capitalize()
            content = message["content"]
            pdf.cell(200, 10, txt=f"{role}: {content}", ln=True)

        return pdf.output(dest='S').encode('latin1')


    # Função para gerar o Excel
    def create_excel(messages):
        df = pd.DataFrame(messages)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue()



    # Função para verificar se a pergunta está relacionada a cadastro
    def is_health_question(prompt):
        keywords = [
        "cadastre-se",
        "cadastro",
        "registro",
        "inscrição",
        "se cadastrar",
        "cadastrar-se",
        "cadastro de usuário",
        "criar conta",
        "criar perfil",
        "criar usuário",
        "criar login",
        "criar senha",
        "criar conta de usuário",
        "registrar",
        "registrar-se",
        "registro de usuário",
        "registro de conta",
        "registrar conta",
        "registrar perfil"
    ]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)


    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./src/img/doutor-chat.jpg", "user": "./src/img/user-chat.jpg"}


    # Replicate Credentials
    with st.sidebar:
        st.markdown(
            """
            <h1 style='text-align: center;'>Doctor Med</h1>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <style>
            .cover-glow {
                width: 100%;
                height: auto;
                padding: 3px;
                box-shadow: 
                    0 0 5px #330000,
                    0 0 10px #660000,
                    0 0 15px #990000,
                    0 0 20px #CC0000,
                    0 0 25px #FF0000,
                    0 0 30px #FF3333,
                    0 0 35px #FF6666;
                position: relative;
                z-index: -1;
                border-radius: 30px;  /* Rounded corners */
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


        # Function to convert image to base64
        def img_to_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()


        # Load and display sidebar image with glowing effect
        img_path = "./src/img/doutor-chat.jpg"
        img_base64 = img_to_base64(img_path)
        st.sidebar.markdown(
            f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")

        os.environ['REPLICATE_API_TOKEN'] = replicate_api
        st.subheader("Adjust model parameters")
        temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.3, step=0.01)
        top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)

        st.sidebar.markdown("---")
        # Load image and convert to base64
        img_path = "./src/img/oraculo-logo.png"  # Replace with the actual image path
        img_base64 = img_to_base64(img_path)

        # Display image with custom CSS class for glowing effect
        st.sidebar.markdown(
            f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
            unsafe_allow_html=True,
        )

        st.sidebar.markdown("---")

    # Inicializar o modelo da Replicate
    llm = Replicate(
        model="meta/meta-llama-3.1-405b-instruct",
        api_token=replicate_api
    )

    # Store LLM-generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{
            "role": "assistant", "content": 'Sou reconhecido como o Doutor Med, fui programado para te responder com uma '
                                            'velocidade extraordinária e passar informações sobre médicos, especialidades,'
                                            'consultas e orientações sobre suplementos e saúde.'}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": 'Sou reconhecido como o Doutor Med, fui programado para te responder com uma '
                                            'velocidade extraordinária e passar informações sobre médicos, especialidades,'
                                            'consultas e orientações sobre suplementos e saúde.'}]


    st.sidebar.button('LIMPAR CONVERSA', on_click=clear_chat_history)
    st.sidebar.caption(
        'Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')
    st.sidebar.caption(
        'Build your own app powered by Arctic and [enter to win](https://arctic-streamlit-hackathon.devpost.com/) $10k in prizes.')

    st.sidebar.markdown("Desenvolvido por [WILLIAM EUSTÁQUIO](https://www.instagram.com/flashdigital.tech/)")

    @st.cache_resource(show_spinner=False)
    def get_tokenizer():
        """Get a tokenizer to make sure we're not sending too much text
        text to the Model. Eventually we will replace this with ArcticTokenizer
        """
        return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


    def get_num_tokens(prompt):
        """Get the number of tokens in a given prompt"""
        tokenizer = get_tokenizer()
        tokens = tokenizer.tokenize(prompt)
        return len(tokens)


    def check_safety(disable=False) -> bool:
        if disable:
            return True

        deployment = get_llamaguard_deployment()
        conversation_history = st.session_state.messages
        user_question = conversation_history[-1]  # pegar a última mensagem do usuário

        prediction = deployment.predictions.create(
            input=template)
        prediction.wait()
        output = prediction.output

        if output is not None and "unsafe" in output:
            return False
        else:
            return True


    # Function for generating Snowflake Arctic response
    def generate_arctic_response():
        prompt = []
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
            else:
                prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")

        prompt.append("<|im_start|>assistant")
        prompt.append("")
        prompt_str = "\n".join(prompt)

        # Verifica se o usuário deseja se cadastrar
        if "quero ser parceiro" in prompt_str.lower() or "desejo criar uma conta de parceiro" in prompt_str.lower() or "conta de parceiro" in prompt_str.lower() or "quero me tornar parceiro" in prompt_str.lower() or "como faço para ser parceiro" in prompt_str.lower() or "quero ter uma conta de parceiro" in prompt_str.lower() or "quero ser um parceiro" in prompt_str.lower():
            st.write("Para se tornar um parceiro na ORÁCULO IA e começar a ter ganhos extraordinários clique no botão abaixo.")
            if st.button("QUERO SER PARCEIRO"):
                showSbconta()
                st.stop()

        # Verifica se o usuário deseja se cadastrar
        if "quero me cadastrar" in prompt_str.lower() or "desejo criar uma conta" in prompt_str.lower() or "criar uma conta" in prompt_str.lower() or "quero este sistema" in prompt_str.lower() or "como faço para me cadastrar" in prompt_str.lower() or "quero ter acesso completo" in prompt_str.lower():
            st.write("Para abrir sua conta na ORÁCULO IA e ter mais poder para analisar dados clique no botão abaixo.")
            if st.button("QUERO CADASTRAR"):
                criar_cliente()
                st.stop()

        if get_num_tokens(prompt_str) >= 128000:  # padrão3072
            st.error(
                "Poxa, você já atingiu seu limite de demostração, mas pode ficar tranquilo. Clique no botão abaixo para "
                "pedir seu acesso.")
            st.button('PEDIR ACESSO', on_click=clear_chat_history, key="clear_chat_history")
            excel_bytes = create_excel(st.session_state.messages)
            pdf_bytes = create_pdf(st.session_state.messages)
            formato_arquivo = st.selectbox("Escolha como deseja baixar sua conversa:", ["PDF", "Excel"])
            if formato_arquivo == "PDF":
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_bytes,
                    file_name="conversa.pdf",
                    mime="application/pdf",
                )
            else:
                st.download_button(
                    label="Baixar Excel",
                    data=excel_bytes,
                    file_name="conversa.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            st.stop()


        for event in replicate.stream(
                "meta/meta-llama-3.1-405b-instruct",
                input={
                    "top_k": 0,
                    "top_p": 1,
                    "prompt": prompt_str,
                    "temperature": 0.1,
                    "system_prompt": system_prompt,
                    "length_penalty": 1,
                    "max_new_tokens": 128000,
                },
        ):
            yield str(event)


    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="./src/img/user-chat.jpg"):
            st.write(prompt)


    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./src/img/doutor-chat.jpg"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)



