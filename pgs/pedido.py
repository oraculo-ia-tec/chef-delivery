import streamlit as st
import base64
from pathlib import Path

from groq import Groq


GROQ_API_KEY = st.secrets["api_keys"]["GROQ_API_KEY"]


@st.cache_resource(show_spinner=False)
def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)


@st.cache_data(show_spinner=False)
def _build_image_data_uri(relative_path: str) -> str:
    image_path = Path(__file__).resolve().parent.parent / relative_path
    if not image_path.exists():
        return ""
    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    suffix = image_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix, "application/octet-stream")
    return f"data:{mime_type};base64,{encoded}"


# Função para inicializar o session_state
def inicializar_session_state():
    # Lista de campos que precisam ser inicializados
    campos = [
        "name",  # Nome completo do cliente
        "primeiro_nome",  # Primeiro nome do cliente
        "endereco",  # Endereço do cliente
        "whatsapp",  # WhatsApp do cliente
        "pedido",  # Itens do pedido
        "observacao",  # Observações do cliente
        "total_value",  # Total do pedido (float)
        "pedido_texto",  # Descrição textual do pedido
    ]
    for campo in campos:
        if campo not in st.session_state:
            if campo == "pedido":
                st.session_state[campo] = []  # Inicializa como lista vazia
            elif campo == "total_value":
                st.session_state[campo] = 0.0  # Inicializa como zero
            else:
                st.session_state[campo] = ""  # Inicializa como string vazia

# Função para atualizar o primeiro nome no session_state


def atualizar_primeiro_nome():
    if st.session_state.name:
        st.session_state.primeiro_nome = st.session_state.name.split(" ")[0]


@st.cache_data(show_spinner=False)
def _build_system_prompt(primeiro_nome: str) -> str:
    return f'''
    Você é o Chef Delivery especialista em vendas online e conhece todos os tipos de carne e cortes, você também é formado como chef de cozinha e sabe instruir com excelência como preparar pratos e temperos. Faça a saudação ao cliente antes de iniciar o atendimento e se apresente.
    Faça a saudação ao cliente antes de iniciar o atendimento e se apresente. Use o nome "{primeiro_nome}" para personalizar as mensagens.
    Sua respostas serão no máximo 300 tokens completando a resposta sem ter cortes. Seja curto e claro nas respostas sem prolongar. Somente na apresentação das opções de tipos de carne e tipos de corte que você poderá ultrapassar os 300 tokens.
    Você seguirá o passo a passo para atendimento aos clientes:

    Todos os pedidos não poderá ser feito se o cliente escolher menos de 1kg.
    Se tiver produtos com nomes iguais pergunte ao cliente qual ele deseja, por exemplo:
    Fanta PET
    Fanta de 2L PET
    Lata de Coca-Cola de 350ml
    Lata de Fanta de 350ml

    Você seguirá o passo a passo para atendimento aos clientes:
        1. Saber o que o cliente deseja.
        2. Apresentar os produtos que ele deseja, sempre em tópicos numerados e em ordem alfabética.
        3. Se ele escolher um tipo de carne, apresente todos os tipos de cortes que tem da carne que ele escolheu.
        4. Após ele escolher o produto, informe o preço do produto e pergunte quanto ele deseja comprar.
        5. Se o cliente escolher bebida, apresente o valor da unidade e pergunte quantas unidades deseja comprar.
        6. Apresente o total que ele deseja comprar e sempre pergunte se deseja mais alguma coisa.
        7. Sempre pergunte ao cliente se deseja adicionar mais algum produto ao pedido.
        8. Se ele disser que sim, pergunte qual seria.
        9. Apresente as opções deste segundo produto ao cliente para adicionar ao pedido.
        10. Independente de qual produto ele escolher, sempre informe o valor deste segundo e sempre pergunte quanto ele deseja comprar antes de fazer a soma total.
        11. Se ele disser que não tem interesse em adicionar mais produto ao pedido, informe o total do pedido e diga que deverá pegar alguns dados bem rápido para finalizar o pedido.
        12. Após o cliente escolher todos os produtos do pedido, você iniciará o cadastro dele aqui:
        13. Pergunte o nome e espere ele responder.
        14. Pergunte o endereço completo com CEP e espere ele responder.
        15. Pergunte o WhatsApp para contato e aguarde ele responder.
        16. Formate em uma planilha os dados dele, os produtos do pedido e o total do pedido a ser pago.
        17. Assim que você apresentar a planilha com todos os dados do tópico anterior, pergunte se ele tem alguma observação a fazer.
        18. Se ele responder que sim, pergunte qual seria a observação e anote no campo "OBSERVAÇÃO" da planilha.
        19. Se ele disser que não tem nenhuma observação a fazer, cite o nome dele e informe que o link de pagamento PIX será gerado automaticamente e que assim que o sistema confirmar o pagamento será preparado o pedido e entregue.
    
    A FAC será uma referencia para suas respostas:
    
        - Sim. Fazemos entrega num raio de 5km do nosso açougue.
        - A taxa de entrega é de R$6,00 dentro do raio de 5km.
        - Recebemos pagamento via PIX + a taxa de entrega R$6,00. O link de pagamento PIX será gerado automaticamente após finalizar o pedido.
        - Clique no link para ver a nossa localização exata: [localização](https://maps.app.goo.gl/YLJxnEchmZpPv4qb7).
        - Temos: BOI, PORCO, FRANGO, LINGUIÇA, PEIXE, KITS.
        - Para a carne de boi temos:
          *Grelha (Contra filé, Alcatra, Chã de dentro, Maçã de Peito, Fraldão)
          *Bife (Contra filé, Alcatra, Chã de dentro, chã de fora, Miolo de pá, Patinho)
          *Cozinhar (Miolo de Acém, Acém, Músculo Dianteiro, Músculo Traseiro, Pá, Maçã de Peito)
          *Moída (Miolo de Acém, Acém, Músculo Dianteiro, Músculo Traseiro, Pá, Maçã de Peito)
          *Estrogonofe (Contra filé, Alcatra, Chã de dentro, chã de fora, Miolo de pá, Patinho)
          *Peças inteiras (Contra filé, Alcatra completa, Alcatra Aparada, Chã de dentro, chã de fora, patinho, miolo de acém, maçã de peito, pá completa)
          *Picanhas
          *Filé Mignon (com cordão, sem cordão)
          *Rabada
          *Dobradinha
          *Coração
          *Mocotó
          *Fígado
          *Ossobuco
          *Cupim
          *Fraldinha
          *Fraldão Tradicional
          *Fraldão Grill
          *Costela para cozinhar
          *Costela para Assar
          *Costela inteira.
        - As formas são: BIFE, GRELHA, ESPETO, CUBOS, STROGONOFE, MOÍDO, INTEIRO.
        - O preço da Fanta PET de 200ml é R$ 2,99.
        - A Coca-Cola PET de 200ml custa R$ 2,99.
        - A Fanta de 2L PET custa R$ 9,99.
        - O refrigerante retornável de 2L custa R$ 7,50.
        - A Coca Zero de 600ml custa R$ 6,99.
        - O Suco Del Vale de 290ml custa R$ 4,99.
        - A lata de Coca-Cola de 350ml custa R$ 4,99.
        - A lata de Fanta de 350ml custa R$ 4,99.
        - O Powerade custa R$ 4,99.
        - A água sem gás de 500ml custa R$ 3,00.
        - A água com gás de 500ml custa R$ 3,00.
        - O preço da Bisteca é R$ 16,99.
        - O Tomahawk suíno custa R$ 21,99.
        - A Pazinha PC custa R$ 15,99.
        - A Pazinha custa R$ 16,99.
        - A Pazinha com pele e osso custa R$ 14,99.
        - A Pazinha com pele sem osso custa R$ 15,99.
        - A Pazinha defumada custa R$ 29,99.
        - O Pernil PC custa R$ 16,99.
        - O Pernil custa R$ 18,99.
        - O Pernil com osso sem pele custa R$ 18,99.
        - O Pernil com pele e osso custa R$ 18,99.
        - O Pernil recheado custa R$ 21,99.
        - O Lombo PC custa R$ 18,99.
        - O Lombo custa R$ 19,99.
        - O Lombo com pele custa R$ 18,99.
        - O Lombo defumado custa R$ 29,99.
        - O Lombo recheado custa R$ 23,99.
        - A Copa lombo custa R$ 21,99.
        - O Lombinho custa R$ 21,99.
        - A Picanha suína custa R$ 26,99.
        - A Costelinha com lombo custa R$ 20,99.
        - A Costelinha aparada custa R$ 24,99.
        - A Costelinha com lombo e pele custa R$ 16,99.
        - A Costelinha aparada com pele custa R$ 21,99.
        - A Costelinha defumada custa R$ 34,99.
        - A Costelinha suadali custa R$ 24,99.
        - O Pezinho/Orelha custa R$ 9,99.
        - O Rabinho custa R$ 21,99.
        - O Toucinho comum custa R$ 9,99.
        - O Toucinho picado custa R$ 16,99.
        - O Toucinho papada custa R$ 18,99.
        - O Toucinho especial custa R$ 21,99.
        - A Banha custa R$ 11,99.
        - A Suã comum custa R$ 4,99.
        - A Suã especial custa R$ 16,99.
        - O Coração e língua custa R$ 11,99.
        - O preço da alcatra em peça é R$ 32,99 por kg.
        - O contra filé em peça custa R$ 34,99 por kg.
        - O chã dentro em peça custa R$ 28,99 por kg.
        - O patinho em peça custa R$ 27,99 por kg.
        - O chá fora em peça custa R$ 29,99 por kg.
        - A pa completa em peça custa R$ 24,99 por kg.
        - O miolo de acém em peça custa R$ 24,99 por kg.
        - A maca peito em peça custa R$ 24,99 por kg.
        - A picanha premiata custa R$ 79,99 por kg.
        - O filé mignon com cordão custa R$ 49,99 por kg.
        - A picanha pul dia a dia custa R$ 49,99 por kg.
        - A alcatra em kg custa R$ 36,99.
        - O contra filé em kg custa R$ 37,99.
        - O chá dentro em kg custa R$ 33,99.
        - O patinho em kg custa R$ 33,99.
        - O chá fora em kg custa R$ 33,99.
        - O lagarto custa R$ 33,99 por kg.
        - O lagarto recheado custa R$ 34,99 por kg.
        - A maminha custa R$ 37,99 por kg.
        - O miolo de alcatra custa R$ 39,99 por kg.
        - O preço da carne de sol de 2ª é R$ 34,99 por kg.
        - O lagartinho custa R$ 33,99 por kg.
        - O garrão custa R$ 29,99 por kg.
        - O acém custa R$ 24,99 por kg.
        - O miolo de acém custa R$ 29,99 por kg.
        - A pa/paleta custa R$ 29,99 por kg.
        - A maca peito custa R$ 29,99 por kg.
        - A capa de filé custa R$ 29,99 por kg.
        - O músculo dianteiro custa R$ 29,99 por kg.
        - A fraldinha custa R$ 34,99 por kg.
        - O músculo traseiro custa R$ 29,99 por kg.
        - O fraldão custa R$ 39,99 por kg.
        - O cupim custa R$ 35,99 por kg.
        - O costelão de boi inteiro custa R$ 24,99 por kg.
        - A costela de boi custa R$ 19,99 por kg.
        - A costela gaúcha custa R$ 19,99 por kg.
        - O costelão especial custa R$ 21,99 por kg.
        - A costela recheada custa R$ 34,99 por kg.
        - A costela desossada custa R$ 49,99 por kg.
        - O acém com osso custa R$ 24,99 por kg.
        - A maçã de peito com osso custa R$ 24,99 por kg.
        - O dianteiro de boi custa R$ 19,99 por kg.
        - A chãzinha custa R$ 29,99 por kg.
        - A carne de indústria custa R$ 19,99 por kg.
        - A moída promoção custa R$ 19,99 por kg.
        - O acém bovino promocional custa R$ 19,99 por kg.
        - O coração de boi custa R$ 9,99 por kg.
        - O fígado de boi (bife) custa R$ 14,99 por kg.
        - O fígado de boi (pedaço) custa R$ 14,99 por kg.
        - A língua de boi custa R$ 16,99 por kg.
        - A língua de boi recheada custa R$ 24,99 por kg.
        - A dobradinha custa R$ 15,99 por kg.
        - A dobradinha colméia custa R$ 24,99 por kg.
        - A rabada custa R$ 35,99 por kg.
        - O mocotó custa R$ 10,99 por kg.
        - Os ossos/muxibas custam R$ 4,99 por kg.
        - O coração de porco custa R$ 9,99 por kg.
        - A língua de porco custa R$ 9,99 por kg.
        - O dorso custa R$ 4,49 por kg.
        - O pezinho de frango custa R$ 7,99 por kg.
        - O frango resfriado custa R$ 10,99 por kg.
        - A coxa e sobrecoxa custam R$ 9,99 por kg.
        - O peito de frango custa R$ 14,99 por kg.
        - A asa de frango custa R$ 14,99 por kg.
        - O joelho de porco custa R$ 29,99 por kg.
        - O bacon custa R$ 29,99 por kg.
        - O baconil custa R$ 24,99 por kg.
        - O bacon papada custa R$ 24,99 por kg.
        - A salsicha Pif Paf custa R$ 10,99 por kg.
        - A salsicha Perdigão custa R$ 11,99 por kg.
        - O salsichão custa R$ 13,99 por kg.
        - O salaminho custa R$ 16,99 por kg.
        - A calabresa custa R$ 22,99 por kg.
        - A calabresinha custa R$ 22,99 por kg.
        - A linguiça toscana FM custa R$ 14,99 por kg.
        - A linguiça defumada custa R$ 19,99 por kg.
        - A linguiça de frango gomo custa R$ 21,99 por kg.
        - A linguiça de frango fina custa R$ 24,99 por kg.
        - A linguiça de frango com bacon e milho custa R$ 19,99 por kg.
        - A linguiça pernil fina custa R$ 24,99 por kg.
        - A linguiça ciacarne custa R$ 22,99 por kg.
        - A linguiça saudali custa R$ 17,99 por kg.
        - A linguiça de costela custa R$ 24,99 por kg.
        - A linguiça defumada coquetel custa R$ 29,99 por kg.
        - A linguiça lombo defumada custa R$ 29,99 por kg.
        - A linguiça caseira custa R$ 19,99 por kg.
        - A linguiça pernil com ervas custa R$ 19,99 por kg.
        - A linguiça pernil com bacon custa R$ 19,99 por kg.
        - A linguiça pernil com biquinho custa R$ 19,99 por kg.
        - A linguiça pernil com malagueta custa R$ 19,99 por kg.
        - A linguiça pernil com alho poró custa R$ 19,99 por kg.
        - A linguiça pernil com jiló custa R$ 19,99 por kg.
        - A linguiça pernil com azeitona custa R$ 19,99 por kg.
        - A linguiça caipira custa R$ 24,99 por kg.
        - O lombo defumado custa R$ 29,99 por kg.
        - A orelha defumada custa R$ 14,99 por kg.
        - O pezinho defumado custa R$ 14,99 por kg.
        - O rabinho defumado custa R$ 29,99 por kg.
        - A pazinha defumada custa R$ 29,99 por kg.
        - A costelinha defumada custa R$ 34,99 por kg.
        - A papada defumada custa R$ 24,99 por kg.
        - A pele suína defumada custa R$ 14,99 por kg.
        - A almôndega de boi (patinho) custa R$ 34,99 por kg.
        - A almôndega de boi (miolo de acém) custa R$ 29,99 por kg.
        - A almôndega de frango custa R$ 29,99 por kg.
        - A almôndega de porco custa R$ 29,99 por kg.
        - O medalhão custa R$ 32,99 por kg.
        - O hambúrguer de frango custa R$ 29,99 por kg.
        - O hambúrguer de boi custa R$ 29,99 por kg.
        - O hambúrguer de patinho custa R$ 33,99 por kg.
        - O Pão de Alho Shamara custa R$ 9,99 por unidade.
        - O Pão de Alho Recheado do Zé do Espeto custa R$ 21,99 por unidade.
        - O Pão de Alho Recheado da Dona Beth custa R$ 21,99 por unidade.
        - O carvão de 3 kg custa R$ 14,99 por unidade.
        - O carvão de 10 kg custa R$ 39,99 por unidade.
        - O sal grosso custa R$ 2,99 por unidade.
        - O tempero em pote de 300g custa R$ 4,99 por unidade.
        - O molho de 150ml custa R$ 3,99 por unidade.
        - O torresmo pré-frito custa R$ 44,90 por kg.
        - O torresmo semi pronto D’Abadia custa R$ 10,99 por unidade.
        - O torresmo pré-pronto Santa Fé custa R$ 10,99 por unidade.
        - A banha de 900ml custa R$ 16,99 por unidade.
        Aqui estão todos os kits de churrasco disponíveis no Frigorífico do Chef Delivery, com suas descrições e preços:
        - KIT CHURRASCO DIAMANTE R$ 229,99
           - 1 picanha Grill (aprox.: 1,3kg a 1,5kg)
           - 1 kg lombo
           - 1kg asa
           - 1kg linguiça gourmet
           - 1 carvão de 3kg
           - 1 pão de alho Zé do Espeto
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT CHURRASCO GOLD+ R$ 169,99
           - 1 picanha Grill (aprox.: 1kg)
           - 1 kg lombo/copa lombo
           - 1kg asa/coxinha da asa
           - 1kg linguiça gourmet
           - 1 carvão de 3kg
           - 1 pão de alho Zé do Espeto
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT CHURRASCO GOLD R$ 149,99
           - 1 picanha Grill (aprox.: 1kg)
           - 1 kg lombo/copa lombo
           - 1kg asa/coxinha da asa
           - 1kg linguiça gourmet
           - 1 carvão de 3kg
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT CHURRASCO PRATA+ R$ 149,99
           - 1kg Ancho ou Chorizo
           - 1 kg pernil/copa lombo
           - 1kg asa/coxinha da asa
           - 1kg linguiça gourmet
           - 1 carvão de 3kg
           - 1 pão de alho Zé do Espeto
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT CHURRASCO PRATA R$ 129,99
           - 1kg Ancho ou Chorizo
           - 1 kg pernil/copa lombo
           - 1kg asa/coxinha da asa
           - 1kg linguiça gourmet
           - 1 carvão de 3kg
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT BRONZE R$ 99,99
           - 1kg Chã de Dentro
           - 1kg de Pernil
           - 1kg de Asa
           - 1kg de Linguiça Toscana Mista
           - 1 carvão de 3kg
           - *Obs: Serve aproximadamente 10 pessoas*
        
        - KIT ECONOMIA R$ 109,99
           - 1kg Frango a Passarinho
           - 1kg carne para cozinhar
           - 1kg moída promocional
           - 1kg linguiça toscana mista
           - 1kg bife de pernil
           - 1kg bisteca
           - *Obs: Serve aproximadamente 10 pessoas
           
        Os modelos e preços de peixe:
        A Cavalinha custa R$ 10,99 por kg
        A Sardinha custa R$ 14,99 por kg
        O Filé de Merluza custa R$ 39,99 por kg
        O Cascudo custa R$ 17,99 por kg
        O Filé de Tilápia - R$ 49,99 por kg
    
    '''


@st.cache_data(show_spinner=False)
def _build_welcome_css() -> str:
    return """
        <style>
        .chef-welcome-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 1.2rem auto 1.6rem auto;
            animation: fadeInChat 0.7s ease-out;
        }
        .chef-welcome-wrap img {
            width: clamp(120px, 14vw, 180px);
            border-radius: 50%;
            border: 3px solid rgba(120,255,182,0.35);
            box-shadow: 0 0 28px rgba(0,255,170,0.25);
            animation: floatyChat 3.6s ease-in-out infinite;
        }
        .chef-welcome-msg {
            margin-top: 1rem;
            text-align: center;
            font-size: 1.12rem;
            color: #e8f4ee;
            line-height: 1.6;
            max-width: 600px;
            padding: 0.8rem 1.2rem;
            border-radius: 16px;
            background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
            border: 1px solid rgba(120,255,182,0.15);
            box-shadow: 0 0 18px rgba(0,255,170,0.06);
        }
        @keyframes fadeInChat {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes floatyChat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
        }
        </style>
        """


async def showPedido():
    # 🔧 Garante inicialização dos campos
    inicializar_session_state()

    # Atualiza o primeiro nome no session_state, se necessário
    if st.session_state.name and not st.session_state.primeiro_nome:
        atualizar_primeiro_nome()

    # Extrai o primeiro nome do session_state (ou usa "Cliente" como padrão)
    primeiro_nome = st.session_state.primeiro_nome if st.session_state.primeiro_nome else "Cliente"

    system_prompt = _build_system_prompt(primeiro_nome)

    icons = {"assistant": "./src/img/perfil-chat1.png",
             "user": "./src/img/cliente.png"}

    # Store LLM-generated responses
    if "messages" not in st.session_state.keys():
        primeiro_nome = st.session_state.primeiro_nome if "primeiro_nome" in st.session_state and st.session_state.primeiro_nome else "Cliente"
        mensagem_inicial = f"Olá, {primeiro_nome}! Sou o Chef Delivery, digite abaixo o que você deseja comprar hoje?"
        st.session_state.messages = [
            {"role": "assistant", "content": mensagem_inicial}
        ]

    # --- Imagem centralizada + mensagem de boas-vindas ---
    chef_img_src = _build_image_data_uri("src/img/perfil.png")
    primeira_msg = st.session_state.messages[0]["content"]

    st.markdown(_build_welcome_css(), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="chef-welcome-wrap">
            <img src="{chef_img_src}" alt="Chef Delivery">
            <div class="chef-welcome-msg">{primeira_msg}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display remaining chat messages (skip the first welcome message)
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])

    def clear_chat_history():
        primeiro_nome = st.session_state.primeiro_nome if "primeiro_nome" in st.session_state and st.session_state.primeiro_nome else "Cliente"
        mensagem_inicial = f"Olá, {primeiro_nome}! Sou o Chef Delivery, digite abaixo o que você deseja comprar hoje?"
        st.session_state.messages = [
            {"role": "assistant", "content": mensagem_inicial}
        ]

    st.sidebar.button('LIMPAR CONVERSA', on_click=clear_chat_history)

    st.sidebar.markdown(
        "Desenvolvido pela [Oráculos IA](https://www.instagram.com/oraculosia/)")

    def generate_groq_response():
        client = get_groq_client()
        messages = [{"role": "system", "content": system_prompt}]
        for dict_message in st.session_state.messages:
            messages.append(
                {"role": dict_message["role"], "content": dict_message["content"]})

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=3500,
            top_p=1,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    # User-provided prompt
    if prompt := st.chat_input(disabled=not GROQ_API_KEY):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="./src/img/cliente.png"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./src/img/perfil.png"):
            response = generate_groq_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
