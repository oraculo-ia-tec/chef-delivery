
import streamlit as st
from transformers import AutoTokenizer
import pandas as pd
import re
#import io
from util import vantagens_oraculo_biblia, missao_visao_valores, localizacao, historia_recomecar, DizimoOferta
import os
import glob
from forms.contact import cadastrar_membro
from langchain.prompts import ChatPromptTemplate
import replicate
import base64
from datetime import datetime, timedelta
from produtos import showProduto

from sqlalchemy import create_engine, text, MetaData
from key_config import DATABASE_URL
from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Integer, Enum, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from textblob import TextBlob  # Para análise de sentimentos
from sqlalchemy.orm import sessionmaker, declarative_base
from util import DizimoOferta


DATABASE_URL = DATABASE_URL
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# Classe para a tabela oraculo_user
class OraculoUser(Base):
    __tablename__ = "oraculo_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cpf_cnpj = Column(String(20))
    email = Column(String(254))
    whatsapp = Column(String(15))
    endereco = Column(String(255))
    cep = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    username = Column(String(50))
    password = Column(String(128))
    image = Column(String(100))
    created_at = Column(DateTime)
    created_time = Column(Time)
    deleted_at = Column(DateTime)
    deleted_time = Column(Time)
    cargo_id = Column(BigInteger)
    decisao = Column(String(50))
    culto_id = Column(BigInteger)
    estado_civil = Column(String(20))
    filhos = Column(Integer)

    # Relacionamentos
    eventos_criados = relationship("OraculoEvento", back_populates="responsavel")
    eventos_participados = relationship("OraculoEventoParticipantes", back_populates="participante")


# Classe para a tabela oraculo_teste
class OraculoTeste(Base):
    __tablename__ = "oraculo_teste"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    usuario = Column(String(255), nullable=False)
    whatsapp = Column(String(20))
    password = Column(String(255), nullable=False)
    cargo_id = Column(BigInteger, nullable=False)


# Classe para a tabela oraculo_produto
class OraculoProduto(Base):
    __tablename__ = "oraculo_produto"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    preco = Column(DECIMAL(10, 2), nullable=False)
    estoque = Column(Integer, default=0)
    imagem = Column(String(255))
    status = Column(Boolean, default=True)  # True = Ativo, False = Inativo
    link = Column(String(500))
    loja_id = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    categoria_id = Column(BigInteger, nullable=False)


# Classe para a tabela oraculo_culto
class OraculoCulto(Base):
    __tablename__ = "oraculo_culto"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome_culto = Column(String(255), nullable=False)
    nome_pregador = Column(String(255))
    titulo_pregacao = Column(String(255))
    diaconato = Column(String(255))
    grupo_louvor = Column(String(255))
    dia_culto = Column(Enum('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    pastor_responsavel = Column(BigInteger)
    departamento_infantil = Column(BigInteger)


# Função para obter produtos por categoria
def obter_produtos_por_categoria():
    with Session() as session:
        query = text("""
            SELECT c.nome AS categoria, p.id, p.nome, p.descricao, p.preco, p.imagem, p.link
            FROM oraculo_produto p
            JOIN categoria_produto c ON p.categoria_id = c.id
        """)
        result = session.execute(query).fetchall()
        produtos_por_categoria = {}
        for row in result:
            categoria, produto_id, nome, descricao, preco, imagem, link = row
            if categoria not in produtos_por_categoria:
                produtos_por_categoria[categoria] = []
            produtos_por_categoria[categoria].append({
                "id": produto_id,
                "nome": nome,
                "descricao": descricao,
                "preco": float(preco),
                "imagem": imagem,
                "link": link
            })
        return produtos_por_categoria


# Função para obter uma sessão do banco de dados
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# --- FUNÇÃO PARA VERIFICAR USUÁRIO E PERMISSÕES ---
def verificar_usuario():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        query = text("SELECT username, password, cargo_id, name, email FROM oraculo_user")
        result = connection.execute(query)
        users = result.fetchall()

        credentials = {
            'usernames': {
                user[0]: {
                    'name': user[3],
                    'password': user[1],
                    'cargo_id': user[2],
                    'email': user[4]
                } for user in users
            }
        }
    return credentials


REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]


dizimo_oferta = DizimoOferta()

def show_mestre_biblia():

    # Inicializa os campos no session_state se não existirem
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'first_name' not in st.session_state:
        # Aqui você pode separar o primeiro nome do nome completo se necessário
        st.session_state.first_name = st.session_state.name.split()[0] if st.session_state.name else ""

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
    if 'cargo' not in st.session_state:
        st.session_state.cargo = ""
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

    if "massages_cul" not in st.session_state:
        st.session_state.massages_cul = []

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

    is_in_registration = False
    is_in_scheduling = False
    is_in_produt = False

    # Função para verificar se a pergunta está relacionada a cadastro
    def is_health_question(prompt):
        keywords = ["cadastrar", "inscrição", "quero me cadastrar", "gostaria de me registrar",
                    "desejo me cadastrar", "quero fazer o cadastro", "quero me registrar", "quero me increver",
                    "desejo me registrar", "desejo me inscrever", "eu quero me cadastrar", "eu desejo me cadastrar",
                    "eu desejo me registrar", "eu desejo me inscrever", "eu quero me registrar",
                    "eu desejo me registrar","eu quero me inscrever"]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Função que analisa desejo de agendar uma reunião
    def is_schedule_meeting_question(prompt):
        keywords = [
            "agendar reunião", "quero agendar uma reunião", "gostaria de agendar uma reunião",
            "desejo agendar uma reunião", "quero marcar uma reunião", "gostaria de marcar uma reunião",
            "desejo marcar uma reunião", "posso agendar uma reunião", "posso marcar uma reunião",
            "Eu gostaria de agendar uma reuniao", "eu quero agendar", "eu quero agendar uma reunião,",
            "quero reunião"
        ]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Função para verificar se a pergunta está relacionada ao interesse em conhecer produtos
    def is_product_interest_question(prompt):
        keywords = [
            "conhecer produtos", "quero ver produtos", "desejo conhecer os produtos",
            "gostaria de ver os produtos", "quero saber mais sobre os produtos",
            "interesse em produtos", "quero conhecer os produtos",
            "eu quero ver os produtos", "eu desejo conhecer os produtos","quais são os produtos da lojas",
            "quero olhar os produtos", "quero saber sobre os produtos","camisa", "segue o plano", "boné", "bone","caneca",
            "garrafa", "térmica","quero gvber os produtos",
        ]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Definir o estudo atual
    estudo = 'Novo Testamento'
    oraculo_biblia = vantagens_oraculo_biblia
    info_historia = historia_recomecar
    info_missao_visao_valore = missao_visao_valores
    info_endereco = localizacao

    def timedelta_to_time(td):
        if isinstance(td, timedelta):
            total_seconds = int(td.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return None

    # Carregar dados das tabelas
    with get_db_session() as session:
        # Consulta direta à tabela oraculo_user
        usuarios_raw = session.execute(
            text("""
            SELECT 
                name, cpf_cnpj, email, whatsapp, endereco, cep, bairro, cidade, username, image,
                created_at, created_time, deleted_at, cargo_id, decisao, culto_id, estado_civil, filhos
            FROM oraculo_user
            WHERE deleted_at IS NULL
            """)
        ).fetchall()

        # Formatar dados dos usuários
        dados_usuarios = [
            f"""
            Nome: {row.name}
            CPF/CNPJ: {row.cpf_cnpj or 'Não informado'}
            Email: {row.email or 'Não informado'}
            WhatsApp: {row.whatsapp or 'Não informado'}
            Endereço: {row.endereco or 'Não informado'}
            CEP: {row.cep or 'Não informado'}
            Bairro: {row.bairro or 'Não informado'}
            Cidade: {row.cidade or 'Não informado'}
            Nome de Usuário: {row.username or 'Não informado'}
            Imagem de Perfil: {row.image or 'Não informado'}
            Data de Cadastro: {row.created_at.strftime('%d/%m/%Y') if row.created_at else 'Não informado'}
            Hora de Cadastro: {timedelta_to_time(row.created_time) if row.created_time else 'Não informado'}
            Cargo ID: {row.cargo_id or 'Não informado'}
            Decisão Espiritual: {row.decisao or 'Não informado'}
            Culto ID: {row.culto_id or 'Não informado'}
            Estado Civil: {row.estado_civil or 'Não informado'}
            Número de Filhos: {row.filhos or 'Não informado'}
            """
            for row in usuarios_raw
        ]
        usuarios_formatados = "\n\n".join(dados_usuarios) if dados_usuarios else "Nenhum usuário cadastrado"

        eventos_raw = session.execute(
            text("""
            SELECT 
                nome_evento, tema_evento, descricao, data_evento, hora_evento, local, tipo_evento, preco, 
                max_participantes, palestrante, created_at
            FROM oraculo_evento
            WHERE status = 1
            """)
        ).fetchall()

        # Formatar dados dos eventos
        dados_eventos = [
            f"""
            Evento: {row.nome_evento}
            Tema: {row.tema_evento or 'Não informado'}
            Descrição: {row.descricao or 'Não informado'}
            Data: {row.data_evento.strftime('%d/%m/%Y') if row.data_evento else 'Não informado'}
            Hora: {timedelta_to_time(row.hora_evento) if row.hora_evento else 'Não informado'}
            Local: {row.local or 'Não informado'}
            Tipo: {row.tipo_evento or 'Não informado'}
            Preço: R$ {f'{row.preco:.2f}' if row.preco else 'Gratuito'}
            Máximo de Participantes: {row.max_participantes or 'Não informado'}
            Palestrante: {row.palestrante or 'Não informado'}
            Data de Cadastro: {row.created_at.strftime('%d/%m/%Y') if row.created_at else 'Não informado'}
            """
            for row in eventos_raw
        ]
        eventos_formatados = "\n\n".join(dados_eventos) if dados_eventos else "Nenhum evento cadastrado"

        enquetes_raw = session.execute(
            text("""
            SELECT 
                titulo, descricao, data_inicio, data_fim, ativo, opcao1, opcao2, opcao3, opcao4, created_dt
            FROM enquete_enquete
            WHERE ativo = 1
            """)
        ).fetchall()

        # Formatar dados das enquetes
        dados_enquetes = [
            f"""
            Título: {row.titulo}
            Descrição: {row.descricao or 'Não informado'}
            Data de Início: {row.data_inicio.strftime('%d/%m/%Y') if row.data_inicio else 'Não informado'}
            Data de Término: {row.data_fim.strftime('%d/%m/%Y') if row.data_fim else 'Não informado'}
            Status: {'Ativa' if row.ativo else 'Inativa'}
            Opções:
                1. {row.opcao1 or 'Não informado'}
                2. {row.opcao2 or 'Não informado'}
                3. {row.opcao3 or 'Não informado'}
                4. {row.opcao4 or 'Não informado'}
            Data de Criação: {row.created_dt.strftime('%d/%m/%Y %H:%M:%S') if row.created_dt else 'Não informado'}
            """
            for row in enquetes_raw
        ]
        enquetes_formatadas = "\n\n".join(dados_enquetes) if dados_enquetes else "Nenhuma enquete cadastrada"

        produtos_raw = session.execute(
            text("""
            SELECT 
                nome, descricao, preco, estoque, imagem, status, categoria_id, link, created_at
            FROM oraculo_produto
            WHERE status = 1
            """)
        ).fetchall()

        # Formatar dados dos produtos
        dados_produtos = [
            f"""
            Produto: {row.nome}
            Descrição: {row.descricao or 'Não informado'}
            Preço: R$ {row.preco:.2f}
            Estoque: {row.estoque or '0'}
            Imagem: {row.imagem or 'Não informado'}
            Status: {'Ativo' if row.status else 'Inativo'}
            Categoria ID: {row.categoria_id or 'Não informado'}
            Link: {row.link or 'Não informado'}
            Data de Cadastro: {row.created_at.strftime('%d/%m/%Y') if row.created_at else 'Não informado'}
            """
            for row in produtos_raw
        ]
        produtos_formatados = "\n\n".join(dados_produtos) if dados_produtos else "Nenhum produto cadastrado"

        categorias_raw = session.execute(
            text("""
            SELECT 
                nome, descricao
            FROM categoria_produto
            """)
        ).fetchall()

        # Formatar dados das categorias
        dados_categorias = [
            f"""
            Categoria: {row.nome}
            Descrição: {row.descricao or 'Não informado'}
            """
            for row in categorias_raw
        ]
        categorias_formatadas = "\n\n".join(dados_categorias) if dados_categorias else "Nenhuma categoria cadastrada"

        cargos_raw = session.execute(
            text("""
                    SELECT 
                        id, name
                    FROM oraculo_cargo
                    """)
        ).fetchall()

        # Formatar dados das categorias
        dados_cargos = [
            f"""
                    Id: {row.id}
                    Nome do Cargo: {row.name}
                    """
            for row in cargos_raw
        ]
        cargos_formatados = "\n\n".join(dados_cargos) if dados_cargos else "Nenhuma categoria cadastrada"

        cultos_raw = session.execute(
            text("""
            SELECT 
                id, nome_culto, nome_pregador, titulo_pregacao, diaconato, grupo_louvor,
                dia_culto, hora_inicio, hora_fim, pastor_responsavel, departamento_infantil
            FROM oraculo_culto
            """)
        ).fetchall()

        # Formatar dados dos cultos
        dados_cultos = [
            f"""
            ID: {row.id}
            Nome do Culto: {row.nome_culto or 'Não informado'}
            Nome do Pregador: {row.nome_pregador or 'Não informado'}
            Título da Pregação: {row.titulo_pregacao or 'Não informado'}
            Diaconato: {row.diaconato or 'Não informado'}
            Grupo de Louvor: {row.grupo_louvor or 'Não informado'}
            Dia do Culto: {row.dia_culto or 'Não informado'}
            Hora de Início: {timedelta_to_time(row.hora_inicio) if row.hora_inicio else 'Não informado'}
            Hora de Término: {timedelta_to_time(row.hora_fim) if row.hora_fim else 'Não informado'}
            Pastor Responsável (ID): {row.pastor_responsavel or 'Não informado'}
            Departamento Infantil: {'Sim' if row.departamento_infantil else 'Não'}
            """
            for row in cultos_raw
        ]
        cultos_formatados = "\n\n".join(dados_cultos) if dados_cultos else "Nenhum culto cadastrado"

        departamentos_raw = session.execute(
            text("""
            SELECT 
                id, departamento, descricao, img, name_lider, created_dt, updated_dt, active_dt
            FROM gestao_departamentos
            WHERE active_dt IS NOT NULL
            """)
        ).fetchall()

        # Formatar dados dos departamentos
        dados_departamentos = [
            f"""
            ID: {row.id}
            Departamento: {row.departamento or 'Não informado'}
            Descrição: {row.descricao or 'Não informado'}
            Imagem: {row.img or 'Não informado'}
            Nome do Líder: {row.name_lider or 'Não informado'}
            Data de Criação: {row.created_dt.strftime('%d/%m/%Y') if row.created_dt else 'Não informado'}
            Última Atualização: {row.updated_dt.strftime('%d/%m/%Y') if row.updated_dt else 'Não informado'}
            Status Ativo Desde: {timedelta_to_time(row.active_dt) if row.active_dt else 'Não informado'}
            """
            for row in departamentos_raw
        ]
        departamentos_formatados = "\n\n".join(
            dados_departamentos) if dados_departamentos else "Nenhum departamento cadastrado"

        # Exemplo para oraculo_teste
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

    dz_domingo_manha = "https://sandbox.asaas.com/c/qt9n57f0y2473pet"  # Dízimo - Culto da Família (09:00 ás 10:30)
    dz_domingo_noite = "https://sandbox.asaas.com/c/xo23koleskzuwosr"  # Dízimo - Culto Profetize (20:00 ás 21:30)
    dz_quinta = "https://sandbox.asaas.com/c/bw5rcpapxmuu4umo"  # Dízimo - Culto de Quinta
    of_domingo_manha = "https://sandbox.asaas.com/c/5h9pqmn4rxsn2cml"  # Oferta - Culto da Família (09:00 ás 10:30)
    of_domingo_noite = "https://sandbox.asaas.com/c/xo23koleskzuwosr"  # Oferta - Culto Profetize (20:00 ás 21:30)
    of_quinta = "https://sandbox.asaas.com/c/i4p70kwrdudodblc"  # Oferta - Culto de Quinta

    # Palavras permitidas
    PALAVRAS_PERMITIDAS = {
        "link": ["link", "enviar link", "qual é o link", "me passe o link"],
        "oferta": ["oferta", "dar oferta", "quero dar uma oferta", "fazer oferta"],
        "dizimo": ["dízimo", "devolver dízimo", "quero devolver meu dízimo", "pagar dízimo"],
        "culto": {
            "domingo_manha": ["domingo de manhã", "culto da manhã", "domingo 9h", "culto família"],
            "domingo_noite": ["domingo à noite", "culto profetize", "domingo 20h"],
            "quinta_noite": ["quinta-feira", "culto de quinta", "quinta à noite"]
        }
    }

    dizimo_oferta = DizimoOferta()

    # Sistema de prompt com dados dinâmicos
    system_prompt = f'''
        Você é o MESTRE BÍBLIA, especialista em análise de dados dos cultos da igreja Comunidade Cristã Recomeçar.
        Suas respostas devem ser diretas e focadas em análise dos dados fornecidos sobre os cultos da igreja.
        Você não prolongará suas respostas para mais de 250 tokens.
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
                    Mestre Bíblia: Olá, {st.session_state.first_name.capitalize()}! Muito prazer em conhecê-lo. 
                    A Recomeçar foi fundada em 2005 pelo pr. Marciano e sua esposa, Maria dos Santos. Em 2006, 
                    o pastor Ronaldo Santos assumiu a liderança e mudou o nome para Comunidade Cristã Recomeçar. 
                    Em 2017, a igreja se mudou para sua sede atual na Av. Dr. João Augusto Fonseca e Silva, 387, 
                    no bairro Novo Eldorado, em Contagem/MG. Você gostaria de saber algo mais específico?
                Exemplo 2 da primeira interação:
                    Usuário:  ola boa tarde
                    Mestre Bíblia: Olá, boa tarde! Como você se chama?
                    Usuário: Meu nome é william eustaquio gomes DA Silva
                    Mestre Bíblia: Olá, {st.session_state.first_name.capitalize()}! Muito prazer em conhecê-lo, como deseja receber a análise dos 
                    cultos da igreja Comunidade Cristã Recomeçar?
                Exemplo 3 da primeira interação:
                    Usuário:  ola boa noite
                    Mestre Bíblia: Olá, boa noite! Como você se chama?
                    Usuário: Meu nome é william eustaquio gomes DA Silva e o seu ?
                    Mestre Bíblia: Olá, {st.session_state.first_name.capitalize()}! Pode me chamar de MESTRE BÍBLIA, especialista em análise de dados 
                    dos cultos da igreja Comunidade Cristã Recomeçar. Como deseja receber a análise?   

            3. Prosiga a conversa normalmente focando somente em responder a análise de dados sobre a 
            Comunidade Cristã Recomeçar: 
                Dados disponíveis:
                - História da igreja: {info_historia}
                - Missão, visão e valores: {info_missao_visao_valore}
                - Endereço: {info_endereco}
                - Cultos: {cultos_formatados}
                - Departamentos: {departamentos_formatados}
                - Produtos: {produtos_formatados}
                - Sistema de gestão: {vantagens_oraculo_biblia}
            4. Use os dados fornecidos para gerar respostas precisas e diretas (máximo 250 tokens).
            5. Seja profissional nas suas respostas e nas análises e não erre.
            6. Não responda perguntas fora do contexto.
            7. Para ofertas/dízimos, verifique o culto antes de enviar links. 

    '''

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
        f"<h1 class='title'>Estude com o <span class='highlight-creme'>MESTRE</span> "
        f"<span class='highlight-dourado'>BÍBLIA</span></h1>",
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
    if "messages_mestre" not in st.session_state.keys():
        st.session_state.messages_mestre = [{
            "role": "assistant", "content": '🌟 Olá! Sou o Mestre Bíblia fui programado para '
                                            'responder suas perguntas sobre a Comunidade Cristã Recomeçar.'}]
    # Dicionário de ícones
    icons = {
        "assistant": "./src/img/mestre-biblia.png",  # Ícone padrão do assistente
        "user": "./src/img/perfil-usuario.png"  # Ícone padrão do usuário
    }

    # Caminho para a imagem padrão
    default_avatar_path = "./src/img/perfil-usuario.png"

    # Função que retorna a imagem do usuário ou a imagem padrão se não houver imagem cadastrada
    def get_avatar_image():
        """Retorna a imagem do usuário ou a imagem padrão se não houver imagem cadastrada."""
        if "image" in st.session_state and st.session_state.image:
            avatar_path = st.session_state.image
            # Verifica se o caminho da imagem realmente existe
            if os.path.exists(avatar_path):
                return avatar_path
            else:
                st.error(f"🚨 Caminho da imagem não encontrado: {avatar_path}")
        return default_avatar_path  # Se a imagem não existir, retorna a padrão

    # Exibição das mensagens no chat
    for message in st.session_state.messages_mestre:
        if message["role"] == "user":
            # Atualiza antes de mostrar a mensagem no chat
            avatar_image = st.session_state.image if st.session_state.image else default_avatar_path
        else:
            avatar_image = icons["assistant"]

        with st.chat_message(message["role"], avatar=avatar_image):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages_mestre = [{
            "role": "assistant", "content": '🌟 Olá! Sou o Mestre Bíblia fui programado para '
                                            'responder suas perguntas sobre a Comunidade Cristã Recomeçar.'}]

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

    def limpar_resposta(resposta):
        """
        Remove tags desnecessárias e saudações duplicadas na resposta do modelo.
        """
        # Remove tags <think>...</think>
        resposta = re.sub(r"<think>.*?</think>", "", resposta, flags=re.DOTALL)

        # Remove <|im_start|> e <|im_end|> junto com seu conteúdo
        resposta = re.sub(r"<\|im_start\|>.*?<\|im_end\|>", "", resposta, flags=re.DOTALL)

        # Remove qualquer resquício de <|im_start|> ou <|im_end|> isolado
        resposta = re.sub(r"<\|im_start\|>|<\|im_end\|>", "", resposta)

        # Remove múltiplos espaços e quebras de linha extras
        resposta = re.sub(r"\s+", " ", resposta).strip()

        # Detecta e remove saudações duplicadas mantendo apenas a primeira
        saudacoes = ["Olá", "Oi", "Boa noite", "Bom dia", "Boa tarde"]
        for saudacao in saudacoes:
            padrao = rf"({saudacao}[\w\s!,.?]*)\1"
            resposta = re.sub(padrao, r"\1", resposta, flags=re.IGNORECASE)

        return resposta.strip()

    def generate_arctic_response():
        try:
            prompt = []
            for dict_message in st.session_state.messages_mestre:
                role = "user" if dict_message["role"] == "user" else "assistant"
                prompt.append(f"<|im_start|>{role}\n{dict_message['content']}<|im_end|>")

            prompt.append("<|im_start|>assistant\n")
            prompt_str = "\n".join(prompt)

            # Inicializa o histórico de mensagens, se não existir
            if "massages_cul" not in st.session_state:
                st.session_state.massages_cul = []

            def stream_generator():
                full_response = ""
                unique_responses = set()  # Armazena partes únicas da resposta
                response_container = st.empty()

                try:
                    for event in replicate.stream(
                            "deepseek-ai/deepseek-r1",
                            input={
                                "top_p": 1,
                                "prompt": system_prompt,
                                "max_tokens": 600,
                                "temperature": 0.1,
                                "presence_penalty": 0,
                                "frequency_penalty": 0
                            },
                    ):
                        current_part = str(event).strip()

                        # Remove tags <think> completamente
                        current_part = re.sub(r"<think>.*?</think>", "", current_part, flags=re.DOTALL).strip()

                        # Verifica se a parte já foi exibida antes
                        if current_part and current_part not in unique_responses:
                            unique_responses.add(current_part)
                            full_response += " " + current_part  # Adiciona com espaço para manter a fluidez

                            # Exibe a resposta limpa em tempo real
                            response_container.markdown(full_response.strip())

                    # Salvar no histórico
                    st.session_state.massages_cul.append({"role": "assistant", "content": full_response.strip()})

                    yield full_response.strip()  # Retorna a resposta final

                except RuntimeError as e:
                    error_message = str(e)
                    if "E1002 PromptTooLong" in error_message:
                        st.info(
                            "⚠️ O limite de mensagem foi atingido! Para continuar, clique no botão **LIMPAR CONVERSA** e reinicie o bate-papo.")
                    elif "Free time limit reached" in error_message:
                        st.info(
                            "⏳ O tempo gratuito da API foi atingido! Para continuar utilizando, configure o faturamento na plataforma Replicate: [Clique aqui](https://replicate.com/account/billing#billing).")
                    else:
                        st.error(f"❌ Erro inesperado: {error_message}")

            return stream_generator()

        except Exception as e:
            st.error(f"❌ Erro inesperado: {str(e)}")
            return iter([])  # Retorna um gerador vazio para evitar erro de iteração

    # User-provided prompt
    if prompt := st.chat_input(disabled=not REPLICATE_API_TOKEN):        # Para o Replicate : REPLICATE_API_TOKEN
        st.session_state.messages_mestre.append({"role": "user", "content": prompt})

        # Chama a função para obter a imagem correta
        avatar_image = get_avatar_image()

        with st.chat_message("user", avatar=avatar_image):
            st.write(prompt)

        # Generate a new response if last message is not from assistant
        if st.session_state.messages_mestre and st.session_state.messages_mestre[-1]["role"] != "assistant":
            with st.chat_message("assistant", avatar="./src/img/mestre-biblia.png"):
                response = generate_arctic_response()
                full_response = st.write_stream(response)
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages_mestre.append(message)

if __name__ == "__main__":
    st.set_page_config(page_title="Mestre Bíblia", page_icon="👥", layout="wide")
    show_mestre_biblia()