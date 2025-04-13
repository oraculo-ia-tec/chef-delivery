import asyncio

import streamlit as st
from transformers import AutoTokenizer
import pandas as pd
import io
from util import vantagens_oraculo_biblia, missao_visao_valores, localizacao, historia_recomecar
import os
import glob
from forms.contact import cadastrar_membro
import json

import replicate
from langchain.llms import Replicate
import base64
from produtos_V2 import cadastrar_produto

from sqlalchemy import create_engine, text, MetaData
from decouple import config
from contextlib import contextmanager
from textblob import TextBlob  # Para análise de sentimentos
from sqlalchemy.orm import sessionmaker, declarative_base
from util import DizimoOferta


REPLICATE_API_TOKEN = config("REPLICATE_API_TOKEN")
DATABASE_URL = config("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# --- FUNÇÃO PARA VERIFICAR USUÁRIO E PERMISSÕES ---
def verificar_usuario():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        query_teste = text("""
                        SELECT usuario AS username, password, email, cargo_id
                        FROM oraculo_teste;
                    """)
        result_teste = connection.execute(query_teste).fetchall()

        credentials = {
            'usernames': {
                user[0]: {
                    'name': user[3],
                    'password': user[1],
                    'cargo_id': user[2],
                    'email': user[4]
                } for user in result_teste
            }
        }
    return credentials


@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def showTeste():

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
    if 'cargo_id' not in st.session_state:
        st.session_state.cargo_id = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'cpf_cnpj' not in st.session_state:
        st.session_state.cpf_cnpj = ""
    if "image" not in st.session_state:
        st.session_state.image = None

    # Inicialização do session state para categorias
    if 'categorias' not in st.session_state:
        st.session_state.categorias = {}

    # Verificando e inicializando os atributos do produto
    if "nome_produto" not in st.session_state:
        st.session_state.nome_produto = ""  # Nome do produto

    if "preco" not in st.session_state:
        st.session_state.preco = 0.0  # Preço do produto

    if "descricao" not in st.session_state:
        st.session_state.descricao = ""  # Descrição do produto

    if "imagem_pro" not in st.session_state:
        st.session_state.imagem_pro = ""  # Caminho da imagem do produto

    if "link" not in st.session_state:
        st.session_state.link = ""  # Link para mais informações sobre o produto

    if "categoria" not in st.session_state:
        st.session_state.categoria = ""  # Categoria do produto

    if "codigo" not in st.session_state:
        st.session_state.codigo = ""  # Código único do produto
        # Inicialização no Streamlit

    def ler_arquivos_txt(pasta):
        """
        Lê todos os arquivos .txt na pasta especificada e retorna uma lista com o conteúdo de cada arquivo.

        Args:
            pasta (str): O caminho da pasta onde os arquivos .txt estão localizados.

        Returns:
            list: Uma lista contendo o conteúdo de cada arquivo .txt.
        """
        conteudos = []  # Lista para armazenar o conteúdo dos arquivos

        # Cria o caminho para buscar arquivos .txt na pasta especificada
        caminho_arquivos = os.path.join(pasta, '*.txt')

        # Usa glob para encontrar todos os arquivos .txt na pasta
        arquivos_txt = glob.glob(caminho_arquivos)

        # Lê o conteúdo de cada arquivo .txt encontrado
        for arquivo in arquivos_txt:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()  # Lê o conteúdo do arquivo
                conteudos.append(conteudo)  # Adiciona o conteúdo à lista

        return conteudos  # Retorna a lista de conteúdos

    # Exemplo de uso da função
    pasta_conhecimento = './conhecimento'  # Caminho da pasta onde os arquivos .txt estão localizados
    conteudos_txt = ler_arquivos_txt(pasta_conhecimento)


    estudo = 'Novo Testamento'
    info_historia = historia_recomecar
    info_missao_visao_valore = missao_visao_valores
    info_endereco = localizacao

    # Carregar dados das tabelas
    with get_db_session() as session:

        # Consulta para oraculo_teste
        testes_raw = session.execute(
            text("""
                SELECT id, email, usuario, whatsapp, cargo_id
                FROM oraculo_teste
                """)
        ).fetchall()

        dados_testes = [
            f"""
                Teste ID: {row.id}
                Email: {row.email}
                Usuário: {row.usuario}
                WhatsApp: {row.whatsapp or 'Não informado'}
                Cargo ID: {row.cargo_id}
                """
            for row in testes_raw
        ]
        testes_formatados = "\n\n".join(dados_testes) if dados_testes else "Nenhum teste cadastrado"

    vantagens_oraculo_biblia = """
        O Oráculo Bíblia oferece uma série de funcionalidades que podem transformar a gestão de uma igreja, tornando-a mais 
        eficiente e organizada. Abaixo estão as explicações detalhadas sobre cada uma dessas funcionalidades, destacando suas 
        vantagens e benefícios.
        
        1. Gestão de Membros:
           A funcionalidade de gestão de membros permite que as igrejas mantenham um registro atualizado de todos os seus 
           integrantes. Isso significa que você pode facilmente acessar informações como nome, contato, histórico de 
           participação e até mesmo dados sobre a contribuição de cada membro. Com isso, é possível promover um acompanhamento 
           mais próximo e personalizado, fortalecendo a comunidade e facilitando o envolvimento dos membros nas atividades da 
           igreja.
        
        2. Gerenciamento de Departamentos:
           Com o gerenciamento de departamentos, as igrejas podem organizar suas atividades em diferentes áreas, como 
           ministérios, grupos de jovens, e serviços sociais. Isso ajuda a distribuir responsabilidades de forma clara e a 
           garantir que cada departamento tenha os recursos e o suporte necessários para funcionar efetivamente. Além disso, 
           facilita a comunicação entre os departamentos, promovendo uma colaboração mais eficaz .
        
        3. Gestão de Cultos:
           A gestão de cultos permite que as igrejas planejem e organizem seus serviços de maneira mais eficiente. É possível 
           programar datas, horários, e temas dos cultos, além de gerenciar a participação dos membros e a logística necessária.
            Isso garante que tudo esteja preparado para oferecer a melhor experiência aos frequentadores, tornando os cultos 
            mais impactantes e bem organizados.
        
        4. Gerenciamento de Enquetes:
           A funcionalidade de gerenciamento de enquetes possibilita que as igrejas coletem feedback dos membros de maneira 
           simples e rápida. Isso pode ser útil para entender as preferências da congregação sobre temas, horários de cultos, e 
           outras atividades. Ao ouvir a voz dos membros, a igreja pode ajustar suas programações e iniciativas para atender 
           melhor às necessidades da comunidade.
        
        5. Gerenciamento de Eventos:
           Com o gerenciamento de eventos, as igrejas podem planejar atividades especiais, como retiros, conferências, e ações 
           comunitárias. Essa funcionalidade ajuda a manter um calendário organizado, controla inscrições e promove uma 
           comunicação clara sobre os eventos, garantindo que os membros estejam sempre informados e engajados.
        
        6. Gestão de Dízimos e Ofertas:
           A gestão de dízimos e ofertas oferece uma maneira prática de monitorar as contribuições financeiras dos membros. Isso
            não apenas facilita a contabilidade da igreja, mas também ajuda a identificar padrões de doação, permitindo que a 
            liderança da igreja planeje melhor suas finanças e projetos. Além disso, isso pode promover uma maior transparência 
            e confiança entre os membros.
        
        7. API com Sistema de Pagamentos (ASAAS):
           Com a integração de uma API que permite transações financeiras seguras, as igrejas podem simplificar o processo de 
           recebimento de dízimos e ofertas. Isso proporciona uma experiência prática para os membros, que podem contribuir de 
           forma rápida e segura, seja presencialmente ou online. Esse tipo de facilidade pode aumentar a participação dos 
           membros nas contribuições.
        
        8. Análise Inteligente com Modelo LLM:
           A análise inteligente utiliza modelos de linguagem para processar e interpretar dados de maneira mais eficaz. Isso 
           permite que as igrejas obtenham insights valiosos sobre a participação dos membros, padrões de doação, e outras 
           métricas relevantes. Com esses dados, a liderança pode tomar decisões mais informadas sobre futuras iniciativas e 
           programas.
        
        9. Automação com Make Automation - Disparo de Emails e Agendamentos:
           A automação é um recurso poderoso que pode economizar tempo e esforço. Com a automação, as igrejas podem programar 
           envios de e-mails, lembretes de eventos, e agendamentos, tudo de forma automática. Isso garante que os membros 
           estejam sempre informados e ajuda a manter a comunicação fluida, sem a necessidade de esforços manuais.
        
            Por que as igrejas devem ter um sistema de gestão eclesiástica como este?
            Em resumo, um sistema de gestão eclesiástica como o oferecido pelo Oráculo Bíblia permite que as igrejas operem de forma
            mais eficiente, economizando tempo e recursos. Ele promove uma melhor organização, comunicação e engajamento entre os 
            membros, facilitando a gestão de atividades e a transparência financeira. Ao adotar esse sistema, as igrejas podem 
            focar em sua missão principal de servir à comunidade, enquanto desfrutam de uma gestão interna mais estruturada e 
            eficaz.
            
        10. Gerenciamento e Gestão de Lojas e Cadastro de Produtos:
            Esta funcionalidade é ideal para igrejas que possuem lojas internas para comercializar produtos cristãos. 
            Com o gerenciamento de lojas, as igrejas podem cadastrar produtos, controlar estoque e registrar vendas de 
            maneira organizada. Isso não só facilita a operação da loja, mas também promove um ambiente mais eficiente 
            para a venda de itens que são úteis para a comunidade, como livros, materiais de estudo e produtos 
            religiosos. Além disso, um sistema de gestão permite que a igreja analise as vendas e o desempenho dos 
            produtos, ajudando na tomada de decisões sobre quais itens oferecer e como melhor atender os anseios dos 
            membros da congregação
        
            """


    # Definição da classe
    class VenderAgendar:
        def __init__(self):
            self.usuario_visualizou_produto = False
            self.usuario_agendou_apresentacao = False

        def to_dict(self):
            """
            Retorna os atributos da classe em um formato serializável (dicionário).
            """
            return {
                "usuario_visualizou_produto": self.usuario_visualizou_produto,
                "usuario_agendou_apresentacao": self.usuario_agendou_apresentacao,
            }

        def from_dict(self, dados):
            """
            Atualiza os atributos da classe a partir de um dicionário.
            """
            self.usuario_visualizou_produto = dados.get("usuario_visualizou_produto", False)
            self.usuario_agendou_apresentacao = dados.get("usuario_agendou_apresentacao", False)

        def vender_produto(self, mensagem_usuario, estudo, testes_formatados, vantagens_oraculo_biblia):
            """
            Analisa a mensagem do usuário para identificar interesse em visualizar produtos.
            Se confirmado, exibe os produtos disponíveis.
            """
            system_prompt_venda = f'''
                Você é MESTRE BÍBLIA, especialista em análise de dados e eventos cristãos.
                Contexto Especial:
                - Se o usuário demonstrar interesse em produtos, indique claramente com 'SIM'.
                - Caso contrário, responda apenas com 'NAO'.
            '''
            prompt = f"""
            {system_prompt_venda}
            Mensagem do usuário: {mensagem_usuario}
            """
            response = generate_arctic_response(prompt, system_prompt_venda)
            decisao = response.strip().upper()

            if decisao == "SIM":
                self.usuario_visualizou_produto = True
                st.info("✅ O usuário deseja visualizar os produtos.")
                self._exibir_produtos()
            else:
                st.warning("⚠️ O usuário não demonstrou interesse em visualizar produtos.")

        def agendar_apresentacao(self, mensagem_usuario, estudo, testes_formatados, vantagens_oraculo_biblia):
            """
            Analisa a mensagem do usuário para identificar interesse em agendar uma apresentação.
            Se confirmado, exibe um formulário de agendamento.
            """
            system_prompt_agenda = f'''
                Você é MESTRE BÍBLIA, especialista em análise de dados e eventos cristãos.
                Contexto Especial:
                - Se o usuário demonstrar interesse em agendamento, indique claramente com 'SIM'.
                - Caso contrário, responda apenas com 'NAO'.
            '''
            prompt = f"""
            {system_prompt_agenda}
            Mensagem do usuário: {mensagem_usuario}
            """
            response = generate_arctic_response(prompt, system_prompt_agenda)
            decisao = response.strip().upper()

            if decisao == "SIM":
                self.usuario_agendou_apresentacao = True
                st.info("✅ O usuário deseja agendar uma apresentação ou consultoria.")
                self._exibir_formulario_agendamento()
            else:
                st.warning("⚠️ O usuário não demonstrou interesse em agendar uma apresentação ou consultoria.")

        def _exibir_produtos(self):
            """
            Exibe os produtos disponíveis no chat.
            """
            st.header("🛍️ Produtos Disponíveis")
            with engine.connect() as connection:
                produtos = connection.execute(text("""
                    SELECT id, nome, descricao, preco, estoque, imagem, link
                    FROM oraculo_produto
                    WHERE status = 1 AND estoque > 0
                """)).fetchall()

            if not produtos:
                st.warning("⚠️ Nenhum produto disponível no momento.")
                return

            cols = st.columns(3)
            for i, produto in enumerate(produtos):
                with cols[i % 3]:
                    st.markdown(f"**{produto.nome}**")
                    st.write(f"💰 R$ {produto.preco:.2f}")
                    st.write(f"📦 Estoque: {produto.estoque}")
                    st.markdown(f"[🔗 Comprar]({produto.link})", unsafe_allow_html=True)

        def _exibir_formulario_agendamento(self):
            """
            Exibe um formulário de agendamento para apresentação ou consultoria.
            """
            st.subheader("📅 Agendar Apresentação ou Consultoria")
            with st.form("form_agendamento", clear_on_submit=True):
                nome = st.text_input("Nome Completo", placeholder="Digite seu nome")
                email = st.text_input("Email", placeholder="Digite seu email")
                telefone = st.text_input("Telefone", placeholder="Digite seu telefone")
                data = st.date_input("Data da Apresentação", min_value=datetime.today())
                horario = st.time_input("Horário da Apresentação")
                mensagem = st.text_area("Mensagem (opcional)", placeholder="Descreva sua necessidade")
                submit_button = st.form_submit_button("Enviar Solicitação")

                if submit_button:
                    if not nome or not email or not telefone:
                        st.error("⚠️ Preencha todos os campos obrigatórios.")
                    else:
                        try:
                            with engine.connect() as connection:
                                query = text("""
                                    INSERT INTO agendamentos (nome, email, telefone, data, horario, mensagem, created_at)
                                    VALUES (:nome, :email, :telefone, :data, :horario, :mensagem, :created_at)
                                """)
                                connection.execute(
                                    query,
                                    {
                                        "nome": nome,
                                        "email": email,
                                        "telefone": telefone,
                                        "data": data,
                                        "horario": horario,
                                        "mensagem": mensagem,
                                        "created_at": datetime.now()
                                    }
                                )
                                connection.commit()
                            st.success("🎉 Sua solicitação foi enviada com sucesso!")
                        except Exception as e:
                            st.error(f"🚨 Erro ao enviar solicitação: {e}")

    if "vender_agendar" not in st.session_state:
        st.session_state.vender_agendar = VenderAgendar().to_dict()

    # Recuperar o objeto VenderAgendar
    vender_agendar = VenderAgendar()
    vender_agendar.from_dict(st.session_state.vender_agendar)

    # Converte o objeto VenderAgendar para um dicionário
    dados_vender_agendar = vender_agendar.to_dict()

    url_dz_of = DizimoOferta

    # Transforma o dicionário em uma string formatada para o system_prompt
    system_prompt = f'''
           Você é o MESTRE BÍBLIA, especialista em análise de dados cristãos e do sistema Oráculo Bíblia.
           Seu foco principal é agendar uma apresentação do sistema a pastores presidentes de igrejas.
           Você também vai tirar dúvidas do usuário que estará interagindo com você sobre o sistema Oráculo Bíblia,
           vai falar sobre suas habilidades e o poder que o sistema Oráculo Bíblia oferece para as igrejas.
           Suas respostas serão precisas e diretas e não prolongue suas respostas para mais de 200 tokens.
           Não responda perguntas fora do contexto e se o usuário insistir não responda nenhuma pergunta sobre outro 
           assunto.
           Use os dados abaixo para análises e recomendações:
           **Estudo Atual:**
            {estudo}
            
            **Testes Cadastrados:**
            {testes_formatados}
            
            **Oráculo Bíblia:**
            {vantagens_oraculo_biblia}
            
            **História da Recomeçar:**
            {info_historia}
            
            **Missão Visão Valores:**
            {info_missao_visao_valore}
            
            **Endereço da Recomeçar:**
            {info_endereco}

           Regras:
           1. Responda com base nos dados fornecidos.
           2. Cumprimente o usuário e pergunte o nome dele. Exemplo da primeira interação:
               Usuário:  Ola boa tarde , você tem informações sobre a Recomeçar?
               Mestre Bíblia: Olá, boa tarde! Sim, tenho informações sobre a Comunidade Cristã Recomeçar. Como você se 
               chama?
               Usuário: Meu nome é william eustaquio gomes
               Mestre Bíblia: Olá, William! Muito prazer em conhecê-lo. 
               A Recomeçar foi fundada em 2005 pelo pr. Marciano e sua esposa, Maria dos Santos. Em 2006, o 
               pr. Ronaldo Santos assumiu a liderança e mudou o nome para Comunidade Cristã Recomeçar. Em 2017, a 
               igreja se mudou para sua sede atual na Av. Dr. João Augusto Fonseca e Silva, 387, no bairro Novo 
               Eldorado, em Contagem/MG. Você gostaria de saber algo mais específico?
                             
           3. Grave o nome dele e o chame sempre pelo primeiro nome para que torne amigável a conversa.
           4. Se não houver dados ou outras informações sobre o usuário peça ele para fazer outra pergunta..
           5. Para perguntas sobre análise de dados use sua experiencia e demonstre métricas cruzadas sobre os 
                dados que você tem.
           6. Use os dados dos cultos para sugerir horários ou responsáveis.
           7. Use os dados dos produtos para sugerir materiais ou recursos.
           8. Faça estudos, pesquisas profundas sobre e responda sempre perguntas bíblicas sobre: **{estudo}** .
           9. Se o usuário quiser devolver o dízimo ou fazer uma oferta passe essas informações: {url_dz_of}

           Contexto Especial:
           - Se o usuário demonstrar interesse em produtos, apresente aqui: 
                {dados_vender_agendar['usuario_visualizou_produto']}.
           - Se o usuário demonstrar interesse em agendamento, apresente o formulário aqui: 
                {dados_vender_agendar['usuario_agendou_apresentacao']}.
        

           Dados do Sistema:
           - Usuário Visualizou Produto: {dados_vender_agendar['usuario_visualizou_produto']}
           - Usuário Agendou Apresentação: {dados_vender_agendar['usuario_agendou_apresentacao']}

           '''


    # Função para gerar as respostas do modelo LLM
    def generate_arctic_response():

        prompt = []
        for dict_message in st.session_state.messages_teste:
            if dict_message["role"] == "user":
                prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
            else:
                prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")

        prompt.append("<|im_start|>assistant")
        prompt.append("")
        prompt_str = "\n".join(prompt)

        for event in replicate.stream(
                "anthropic/claude-3.7-sonnet",
                input={
                    "top_k": 0,
                    "top_p": 1,
                    "prompt": prompt_str,
                    "temperature": 0.1,
                    "system_prompt": system_prompt,
                    "length_penalty": 1,
                    "max_new_tokens": 4096,
                },
        ):
            yield str(event)


    st.markdown(
        """
        <style>
        .highlight-creme {
            background: linear-gradient(90deg, #f5f5dc, gold);  /* Gradiente do creme para dourado */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        .highlight-dourado {
            background: linear-gradient(90deg, gold, #f5f5dc);  /* Gradiente do dourado para creme */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título da página
    st.markdown(
        f"<h1 class='title'>Estude com o <span class='highlight-creme'>MESTRE</span> <span class='highlight-dourado'>"
        f"BÍBLIA</span></h1>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow: 
                0 0 5px rgba(255, 255, 255, 0.9), /* Efeito de brilho suave */
                0 0 10px rgba(255, 255, 255, 0.4),
                0 0 15px rgba(255, 255, 255, 0.3),
                0 0 20px rgba(255, 255, 255, 0.2),
                0 0 25px rgba(255, 255, 255, 0.1);
            position: relative;
            z-index: -1;
            border-radius: 30px;  /* Cantos arredondados */
            background-color: rgba(255, 255, 255, 0.1); /* Fundo levemente branco */
            border: 5px solid rgba(255, 255, 255, 0.6); /* Borda mais grossa e branca */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Dicionário de ícones
    icons = {
        "assistant": "./src/img/mestre-biblia.png",  # Ícone padrão do assistente
        "user": "./src/img/perfil-usuario.png"  # Ícone padrão do usuário
    }

    # Caminho para a imagem padrão
    default_avatar_path = "./src/img/perfil-usuario.png"

    # Inicialização do st.session_state.messages_teste
    if "messages_teste" not in st.session_state:
        st.session_state.messages_teste = []

    # Exibição das mensagens
    for message in st.session_state.messages_teste:
        if message["role"] == "user":
            # Verifica se a imagem do usuário existe
            avatar_image = st.session_state.image if "image" in st.session_state and st.session_state.image else (
                default_avatar_path)
        else:
            avatar_image = icons["assistant"]  # Ícone padrão do assistente

        with st.chat_message(message["role"], avatar=avatar_image):
            st.write(message["content"])

    # Function to convert image to base64
    def img_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    st.sidebar.markdown("---")

    # Load and display sidebar image with glowing effect
    img_path = "./src/img/mestre-biblia.png"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )


    # Store LLM-generated responses
    if "messages_teste" not in st.session_state.keys():
        st.session_state.messages_teste = [{
            "role": "assistant", "content": '🌟 Bem-vindo ao Mestre Bíblia!Estou pronto para ajudá-lo a testar o '
                                            'sistema, fazer estudo das Escrituras Sagradas e tirar suas dúvidas sobre '
                                            'e agendar uma apresentação com o desenvolvedor responsável'}]

    # Dicionário de ícones
    icons = {
        "assistant": "./src/img/mestre-biblia.png",  # Ícone padrão do assistente
        "user": "./src/img/perfil-usuario.png"  # Ícone padrão do usuário
    }

    # Caminho para a imagem padrão
    default_avatar_path = "./src/img/perfil-usuario.png"

    # Exibição das mensagens
    for message in st.session_state.messages_teste:
        if message["role"] == "user":
            # Verifica se a imagem do usuário existe
            avatar_image = st.session_state.imagem if "imagem" in st.session_state and st.session_state.imagem else default_avatar_path
        else:
            avatar_image = icons["assistant"]  # Ícone padrão do assistente

        with st.chat_message(message["role"], avatar=avatar_image):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages_teste = [{
            "role": "assistant", "content": '🌟 Bem-vindo ao Mestre Bíblia!Estou pronto para ajudá-lo a testar o '
                                            'sistema, fazer estudo das Escrituras Sagradas e tirar suas dúvidas sobre '
                                            'e agendar uma apresentação com o desenvolvedor responsável'}]

    st.sidebar.markdown("---")

    st.sidebar.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

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

    def get_avatar_image():
        """Retorna a imagem do usuário ou a imagem padrão se não houver imagem cadastrada."""
        if st.session_state.image is not None:
            return st.session_state.image  # Retorna a imagem cadastrada
        else:
            return default_avatar_path  # Retorna a imagem padrão

    # User-provided prompt
    if prompt := st.chat_input(disabled=not REPLICATE_API_TOKEN):
        st.session_state.messages_teste.append({"role": "user", "content": prompt})

        # Chama a função para obter a imagem correta
        avatar_image = get_avatar_image()

        with st.chat_message("user", avatar=avatar_image):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages_teste and st.session_state.messages_teste[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./src/img/mestre-biblia.png"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages_teste.append(message)


# Este código só será executado se o arquivo for executado diretamente
if __name__ == "__main__":
    st.set_page_config(page_title='ORACULO BÍBLIA', page_icon="📜", layout="wide")
    showTeste()