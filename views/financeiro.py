import streamlit as st
import replicate
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import re
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from decouple import config
import requests


from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine, text
from sqlalchemy import (create_engine, Column, BigInteger, String, Text, DECIMAL, Integer, Boolean, DateTime,
                        ForeignKey, text, func, Float, Enum, Numeric, Time,Date )

# Configuração da API do Asaas
BASE_URL_ASAAS = config("BASE_URL_ASAAS")
ASAAS_API_KEY = config("ASAAS_API_KEY")

# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class OraculoEvento(Base):
    __tablename__ = "oraculo_evento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_evento = Column(String(100), nullable=False)
    tema_evento = Column(String(100))
    descricao = Column(Text)
    data_evento = Column(DateTime)
    hora_evento = Column(String(8))  # HH:MM:SS
    hora_termino = Column(String(8))  # HH:MM:SS
    local = Column(String(255))
    tipo_evento = Column(Enum("gratuito", "pago"), nullable=False)
    valor = Column(Float)  # Alterado para Float
    max_participantes = Column(Integer)
    palestrante = Column(String(100))
    biografia_palestrante = Column(Text)
    foto_palestrante = Column(String(255))
    contato_email = Column(String(254))
    contato_whatsapp = Column(String(20))
    facebook_url = Column(String(255))
    instagram_url = Column(String(255))
    linkedin_url = Column(String(255))
    banner = Column(String(255))
    responsavel_id = Column(Integer, ForeignKey("usuario.id"))  # Supondo uma tabela 'usuario'
    status = Column(Enum("agendado", "cancelado", "realizado"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cargo_permitido = Column(Integer, ForeignKey("cargo.id"))  # Supondo uma tabela 'cargo'

    # Relacionamentos
    responsavel = relationship("Usuario", back_populates="eventos")  # Exemplo de relacionamento
    cargo = relationship("Cargo", back_populates="eventos_permitidos")


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
    created_at = Column(Date)
    created_time = Column(Time)
    deleted_at = Column(Date)
    deleted_time = Column(Time)
    cargo_id = Column(BigInteger)
    decisao = Column(String(50))
    culto_id = Column(BigInteger)
    estado_civil = Column(String(20))
    filhos = Column(Integer)

    # Relacionamento inverso
    eventos = relationship("OraculoEvento", back_populates="responsavel")


class OraculoProduto(Base):
    __tablename__ = "oraculo_produto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    valor = Column(Float)
    estoque = Column(Integer, nullable=False)
    imagem = Column(String(255))
    status = Column(Integer)  # 1 = ativo, 0 = inativo
    link = Column(String(500))
    loja_id = Column(Integer, ForeignKey("lojas.id"))  # Supondo uma tabela 'lojas'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    categoria_id = Column(Integer, ForeignKey("categoria.id"))  # Supondo uma tabela 'categoria'

    # Relacionamentos
    loja = relationship("Loja", back_populates="produtos")
    categoria = relationship("Categoria", back_populates="produtos")


class Dizimo(Base):
    __tablename__ = "dizimo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_total = Column(Float)
    link = Column(String(255))
    qrcode = Column(String(255))
    oraculo_culto_id = Column(Integer, ForeignKey("culto.id"))  # Supondo uma tabela 'culto'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    culto = relationship("Culto", back_populates="dizimos")  # Exemplo de relacionamento


class Oferta(Base):
    __tablename__ = "oferta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_total = Column(Float)
    link = Column(String(255))
    qrcode = Column(String(255))
    oraculo_culto_id = Column(Integer, ForeignKey("culto.id"))  # Supondo uma tabela 'culto'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    culto = relationship("Culto", back_populates="ofertas")  # Exemplo de relacionamento


class Financeiro(Base):
    __tablename__ = "financeiro"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum("dizimo", "oferta", "evento", "produto"), nullable=False)  # Tipo de transação
    valor = Column(Float)
    status = Column(Enum("pendente", "pago", "cancelado"), nullable=False)
    metodo_pagamento = Column(Enum("pix", "cartao", "boleto"), nullable=False)
    referencia_id = Column(Integer, nullable=False)  # ID da tabela relacionada (ex.: dizimo.id, oferta.id)
    referencia_tabela = Column(String(50), nullable=False)  # Nome da tabela relacionada (ex.: "dizimo", "oferta")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos (exemplos)
    # dizimo = relationship("Dizimo", foreign_keys=[referencia_id], primaryjoin="Financeiro.referencia_id == Dizimo.id")
    # oferta = relationship("Oferta", foreign_keys=[referencia_id], primaryjoin="Financeiro.referencia_id == Oferta.id")


def adicionar_transacao(session, tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela):
    transacao = Financeiro(
        tipo=tipo,
        valor=valor,
        status=status,
        metodo_pagamento=metodo_pagamento,
        referencia_id=referencia_id,
        referencia_tabela=referencia_tabela
    )
    session.add(transacao)
    session.commit()
    return transacao


def listar_transacoes(session, tipo=None, status=None):
    query = session.query(Financeiro)
    if tipo:
        query = query.filter(Financeiro.tipo == tipo)
    if status:
        query = query.filter(Financeiro.status == status)
    return query.all()


def validar_referencia(session, referencia_id, referencia_tabela):
    """
    Verifica se o `referencia_id` existe na tabela especificada por `referencia_tabela`.
    """
    if referencia_tabela == "oraculo_evento":
        query = text("SELECT id FROM oraculo_evento WHERE id = :referencia_id")
    elif referencia_tabela == "oraculo_produto":
        query = text("SELECT id FROM oraculo_produto WHERE id = :referencia_id")
    elif referencia_tabela == "dizimo":
        query = text("SELECT id FROM dizimo WHERE id = :referencia_id")
    elif referencia_tabela == "oferta":
        query = text("SELECT id FROM oferta WHERE id = :referencia_id")
    else:
        raise ValueError(f"Tabela desconhecida: {referencia_tabela}")

    result = session.execute(query, {"referencia_id": referencia_id}).fetchone()
    if not result:
        raise ValueError(f"Referência inválida: ID {referencia_id} não encontrado na tabela {referencia_tabela}")
    return True


def salvar_transacao(session, tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id):
    # Validar a referência
    validar_referencia(session, referencia_id, referencia_tabela)

    # Inserir a transação
    query = text("""
        INSERT INTO financeiro (
            tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id
        ) VALUES (
            :tipo, :valor, :status, :metodo_pagamento, :referencia_id, :referencia_tabela, :usuario_id
        )
    """)
    session.execute(
        query,
        {
            "tipo": tipo,
            "valor": valor,
            "status": status,
            "metodo_pagamento": metodo_pagamento,
            "referencia_id": referencia_id,
            "referencia_tabela": referencia_tabela,
            "usuario_id": usuario_id
        }
    )
    session.commit()


def criar_link_pagamento(
    name: str,
    description: str,
    value: float,
    endDate: str,
    billingType: str = "UNDEFINED",
    chargeType: str = "DETACHED",
    dueDateLimitDays: int = 10,
    maxInstallmentCount: int = 1,
    externalReference: str = None,
    notificationEnabled: bool = False,
    isAddressRequired: bool = True,
):
    """
    Cria um link de pagamento no Asaas.

    Args:
        name (str): Nome do link de pagamento.
        description (str): Descrição do link de pagamento.
        value (float): Valor do pagamento.
        endDate (str): Data de expiração do link (formato YYYY-MM-DD).
        billingType (str): Tipo de cobrança ("UNDEFINED", "BOLETO", "PIX").
        chargeType (str): Tipo de cobrança ("DETACHED", "REPEAT").
        dueDateLimitDays (int): Número de dias para o vencimento.
        maxInstallmentCount (int): Número máximo de parcelas.
        externalReference (str): Referência externa (opcional).
        notificationEnabled (bool): Habilita notificações.
        isAddressRequired (bool): Define se o endereço é obrigatório.

    Returns:
        dict: Resposta da API contendo os detalhes do link de pagamento.
    """
    url = f"{BASE_URL}/paymentLinks"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_API_KEY,
    }
    payload = {
        "name": name,
        "description": description,
        "value": value,
        "endDate": endDate,
        "billingType": billingType,
        "chargeType": chargeType,
        "dueDateLimitDays": dueDateLimitDays,
        "maxInstallmentCount": maxInstallmentCount,
        "externalReference": externalReference,
        "notificationEnabled": notificationEnabled,
        "isAddressRequired": isAddressRequired,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Levanta erro para respostas HTTP inválidas
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar link de pagamento: {e}")
        return None


def adicionar_imagem_ao_link(link_id: str, imagem_path: str):
    """
    Adiciona uma imagem ao link de pagamento no Asaas.

    Args:
        link_id (str): ID do link de pagamento.
        imagem_path (str): Caminho local da imagem a ser enviada.

    Returns:
        dict: Resposta da API contendo os detalhes da imagem adicionada.
    """
    url = f"{BASE_URL}/paymentLinks/{link_id}/images"
    headers = {
        "accept": "application/json",
        "access_token": ASAAS_API_KEY,
    }

    try:
        with open(imagem_path, "rb") as image_file:
            files = {"file": (imagem_path, image_file)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()  # Levanta erro para respostas HTTP inválidas
            return response.json()
    except FileNotFoundError:
        print("Erro: Arquivo de imagem não encontrado.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao adicionar imagem ao link de pagamento: {e}")
        return None


# Funções auxiliares
def criar_link_pagamento(name, description, value, endDate, billingType="UNDEFINED", chargeType="DETACHED"):
    """
    Cria um link de pagamento no Asaas.
    """
    url = "https://api-sandbox.asaas.com/v3/paymentLinks"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_API_KEY,
    }
    payload = {
        "name": name,
        "description": description,
        "value": value,
        "endDate": endDate,
        "billingType": billingType,
        "chargeType": chargeType,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao criar link de pagamento: {e}")
        return None


def adicionar_imagem_ao_link(link_id, imagem_path):
    """
    Adiciona uma imagem ao link de pagamento no Asaas.
    """
    url = f"https://api-sandbox.asaas.com/v3/paymentLinks/{link_id}/images"
    headers = {
        "accept": "application/json",
        "access_token": ASAAS_API_KEY,
    }

    try:
        with open(imagem_path, "rb") as image_file:
            files = {"file": (imagem_path, image_file)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
    except FileNotFoundError:
        st.error("Erro: Arquivo de imagem não encontrado.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao adicionar imagem ao link: {e}")
        return None


def salvar_transacao_financeira(tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id):
    """
    Salva uma transação financeira no banco de dados.
    """
    query = """
        INSERT INTO financeiro (
            tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id
        ) VALUES (
            :tipo, :valor, :status, :metodo_pagamento, :referencia_id, :referencia_tabela, :usuario_id
        )
    """
    try:
        with Session() as session:
            session.execute(
                text(query),
                {
                    "tipo": tipo,
                    "valor": valor,
                    "status": status,
                    "metodo_pagamento": metodo_pagamento,
                    "referencia_id": referencia_id,
                    "referencia_tabela": referencia_tabela,
                    "usuario_id": usuario_id,
                },
            )
            session.commit()
            return True
    except Exception as e:
        st.error(f"Erro ao salvar transação financeira: {e}")
        return False


def listar_transacoes_financeiras():
    """
    Lista todas as transações financeiras cadastradas no banco de dados.
    """
    query = """
        SELECT id, tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id
        FROM financeiro
    """
    try:
        with Session() as session:
            result = session.execute(text(query)).fetchall()
            return result
    except Exception as e:
        st.error(f"Erro ao listar transações financeiras: {e}")
        return []


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


# Interface Principal
def showFinanceiro():
    st.title("💰 Gerenciamento Financeiro")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "➕ Cadastrar Transação",
            "📋 Listar Transações",
            "✏️ Editar/Excluir",
            "📊 Estatísticas Financeiras",
            "📈 Análise Inteligente",
        ]
    )

    # 📝 **Aba de Cadastro**
    with tab1:
        st.header("➕ Cadastrar Nova Transação Financeira")

        with st.form("form_cadastro_financeiro", clear_on_submit=True, border=True):
            col1, col2 = st.columns(2)

            with col1:
                tipo = st.selectbox("Tipo de Transação", ["dizimo", "oferta", "evento", "produto"])
                valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
                status = st.selectbox("Status", ["pendente", "pago", "cancelado"])
                metodo_pagamento = st.selectbox("Método de Pagamento", ["pix", "cartao", "boleto"])

            with col2:
                referencia_id = st.number_input("ID da Referência", min_value=1, step=1)
                referencia_tabela = st.selectbox(
                    "Tabela de Referência", ["dizimo", "oferta", "oraculo_evento", "oraculo_produto"]
                )
                usuario_id = st.number_input("ID do Usuário", min_value=1, step=1)

            submitted = st.form_submit_button("✅ Cadastrar Transação")
            if submitted:
                if not all([tipo.strip(), valor > 0, status.strip(), metodo_pagamento.strip()]):
                    st.error("⚠️ Preencha todos os campos obrigatórios.")
                else:
                    sucesso = salvar_transacao_financeira(
                        tipo, valor, status, metodo_pagamento, referencia_id, referencia_tabela, usuario_id
                    )
                    if sucesso:
                        st.success("🎉 Transação financeira cadastrada com sucesso!")
                        st.balloons()
                    else:
                        st.error("⚠️ Falha ao salvar a transação financeira.")

    # 📦 **Aba de Listagem de Transações**
    with tab2:
        st.subheader("📋 Visualizar Transações Financeiras Cadastradas")
        transacoes = listar_transacoes_financeiras()

        if not transacoes:
            st.info("⚠️ Nenhuma transação financeira cadastrada.")
        else:
            for transacao in transacoes:
                with st.expander(f"📌 ID: {transacao.id} - Tipo: {transacao.tipo}"):
                    st.write(f"**Valor:** R$ {transacao.valor:.2f}")
                    st.write(f"**Status:** {transacao.status}")
                    st.write(f"**Método de Pagamento:** {transacao.metodo_pagamento}")
                    st.write(f"**Referência ID:** {transacao.referencia_id}")
                    st.write(f"**Tabela de Referência:** {transacao.referencia_tabela}")
                    st.write(f"**Usuário ID:** {transacao.usuario_id}")
                    st.divider()

    # ✏️ **Aba de Edição/Exclusão**
    with tab3:
        st.header("✏️ Editar ou Excluir Transação Financeira")
        transacoes = listar_transacoes_financeiras()

        if not transacoes:
            st.info("⚠️ Nenhuma transação financeira disponível para edição/exclusão.")
        else:
            transacao_selecionada = st.selectbox(
                "Selecione uma transação para editar/excluir", [t.id for t in transacoes]
            )
            nova_descricao = st.text_input("Nova Descrição")
            novo_valor = st.number_input("Novo Valor (R$)", min_value=0.01, format="%.2f")

            if st.button("✅ Atualizar Transação"):
                # Lógica para atualizar a transação no banco de dados
                st.success("🎉 Transação atualizada com sucesso!")

            if st.button("🗑️ Excluir Transação"):
                # Lógica para excluir a transação do banco de dados
                st.success("✅ Transação excluída com sucesso!")

    # 📊 **Aba de Estatísticas Financeiras**
    with tab4:
        st.header("📊 Estatísticas Financeiras")
        transacoes = listar_transacoes_financeiras()

        if not transacoes:
            st.info("⚠️ Nenhuma transação financeira disponível para análise.")
        else:
            valores = [float(t.valor) for t in transacoes]
            total_transacoes = len(transacoes)
            valor_total = sum(valores)
            valor_medio = valor_total / total_transacoes if total_transacoes > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Transações", total_transacoes)
            with col2:
                st.metric("Valor Total (R$)", f"{valor_total:.2f}")
            with col3:
                st.metric("Valor Médio (R$)", f"{valor_medio:.2f}")

    # 📈 **Aba de Análise Inteligente**
    with tab5:
        st.header("📈 Análise Inteligente - Financeiro Recomeçar")
        # Consultar dados do banco de dados
        with Session() as session:
            # Consulta para obter dízimos
            dizimos = session.execute(text("""
                SELECT valor_total, created_at
                FROM dizimo
            """)).fetchall()

            # Consulta para obter ofertas
            ofertas = session.execute(text("""
                SELECT valor_total, created_at
                FROM oferta
            """)).fetchall()

            # Consulta para obter eventos pagos
            eventos_pagos = session.execute(text("""
                SELECT nome_evento, preco, data_evento
                FROM oraculo_evento
                WHERE tipo_evento = 'pago'
            """)).fetchall()

            # Consulta para obter produtos vendidos
            produtos_vendidos = session.execute(text("""
                SELECT nome, preco, estoque
                FROM oraculo_produto
                WHERE status = 1
            """)).fetchall()

            # Estatísticas agregadas
            total_dizimos = sum(float(d[0]) for d in dizimos) if dizimos else 0
            total_ofertas = sum(float(o[0]) for o in ofertas) if ofertas else 0
            total_eventos_pagos = sum(float(e[1]) if e[1] is not None else 0.0 for e in eventos_pagos) if eventos_pagos else 0.0
            total_produtos_vendidos = sum(
                float(p[1]) * (100 - p[2]) for p in produtos_vendidos) if produtos_vendidos else 0.0

        # Estruturar os dados para análise
        dados_analise = {
            "total_dizimos": total_dizimos,
            "total_ofertas": total_ofertas,
            "total_eventos_pagos": total_eventos_pagos,
            "total_produtos_vendidos": total_produtos_vendidos,
            "dizimos": [
                {
                    "valor": float(d[0]),
                    "data": d[1].strftime("%d/%m/%Y") if d[1] else None
                }
                for d in dizimos
            ],
            "ofertas": [
                {
                    "valor": float(o[0]),
                    "data": o[1].strftime("%d/%m/%Y") if o[1] else None
                }
                for o in ofertas
            ],
            "eventos_pagos": [
                {
                    "nome_evento": e[0],
                    "valor": float(e[1]),
                    "data_evento": e[2].strftime("%d/%m/%Y") if e[2] else None
                }
                for e in eventos_pagos
            ],
            "produtos_vendidos": [
                {
                    "nome": p[0],
                    "valor": float(p[1]),
                    "estoque": p[2]
                }
                for p in produtos_vendidos
            ]
        }

        # Formatar os dados para o modelo
        dados_formatados = ""
        dados_formatados += "\n- Detalhes dos Dízimos:\n"
        for dizimo in dados_analise["dizimos"]:
            dados_formatados += f"""
                - Valor: R$ {dizimo['valor']:.2f}
                  Data: {dizimo['data']}
                """

        dados_formatados += "\n- Detalhes das Ofertas:\n"
        for oferta in dados_analise["ofertas"]:
            dados_formatados += f"""
                - Valor: R$ {oferta['valor']:.2f}
                  Data: {oferta['data']}
                """

        dados_formatados += "\n- Detalhes dos Eventos Pagos:\n"
        for evento in dados_analise["eventos_pagos"]:
            dados_formatados += f"""
                - Nome do Evento: {evento['nome_evento']}
                  Valor: R$ {evento['valor']:.2f}
                  Data: {evento['data_evento']}
                """

        dados_formatados += "\n- Detalhes dos Produtos Vendidos:\n"
        for produto in dados_analise["produtos_vendidos"]:
            dados_formatados += f"""
                - Produto: {produto['nome']}
                  Valor Unitário: R$ {produto['valor']:.2f}
                  Estoque Restante: {produto['estoque']}
                """

        # Sistema de prompt com dados dinâmicos
        system_prompt = f'''
        Você é MESTRE BÍBLIA, especialista em análise de dados financeiros igreja Comunidade Cristã Recomeçar.
        Suas respostas devem ser diretas e focadas em análise dos dados fornecidos sobre o financeiro da igreja.
        Você não prolongará suas respostas para mais de 250 tokens.
        Não responda perguntas fora do contexto e se o usuário insistir não responda nenhuma pergunta sobre outro 
        assunto.
        
        Regras:
            1. Responda com base nos dados fornecidos da igreja sobre o financeiro.
            2. Cumprimente o usuário e pergunte o nome dele. 
                Exemplo 1 da primeira interação:
                    Usuário:  Ola bom dia , você tem informações sobre a Recomeçar?
                    Mestre Bíblia: Olá, boa tarde! Sim, tenho informações sobre a Comunidade Cristã Recomeçar. Como você se 
                    chama?
                    Usuário: Meu nome é william eustaquio gomes DA Silva
                    Mestre Bíblia: Olá, William! Muito prazer em conhecê-lo. 
                    A Recomeçar foi fundada em 2005 pelo pr. Marciano e sua esposa, Maria dos Santos. Em 2006, o 
                    pr. Ronaldo Santos assumiu a liderança e mudou o nome para Comunidade Cristã Recomeçar. Em 2017, a 
                    igreja se mudou para sua sede atual na Av. Dr. João Augusto Fonseca e Silva, 387, no bairro Novo 
                    Eldorado, em Contagem/MG. Você gostaria de saber algo mais específico?
                Exemplo 2 da primeira interação:
                    Usuário:  ola boa tarde
                    Mestre Bíblia: Olá, boa tarde!Como você se chama?
                    Usuário: Meu nome é william eustaquio gomes DA Silva
                    Mestre Bíblia: Olá, William! Muito prazer em conhecê-lo, como deseja receber a análise financeira 
                    hoje?
                Exemplo 3 da primeira interação:
                    Usuário:  ola boa noite
                    Mestre Bíblia: Olá, boa noite!Como você se chama?
                    Usuário: Meu nome é william eustaquio gomes DA Silva e o seu ?
                    Mestre Bíblia: Olá, William! Pode me chamar de MESTRE BÍBLIA, especialista em análise de dados 
                    financeiros da igreja Comunidade Cristã Recomeçar. como deseja receber a análise financeira 
                    hoje?   
                    
            3. Prosiga a conversa normalmente focando somente em responder a análise de dados financeiros: 
                {dados_formatados}.
            4. Seja profissional nas suas respostas e nas análises e não erre.
            5. Não liste todas as transações automaticamente, a menos que o usuário peça.
            6. Para perguntas sobre o financeiro, faça análise cruzada entre as tabelas.  
            
            '''

        # Set a default model
        if "deepseek_model" not in st.session_state:
            st.session_state["deepseek_model"] = "deepseek-ai/deepseek-r1"

        # Set a default model
        if "claude_model" not in st.session_state:
            st.session_state["claude_model"] = "anthropic/claude-3.7-sonnet"

        # Interface do chat
        if "massages_fin" not in st.session_state:
            st.session_state.massages_fin = []

        # Contêiner para o histórico de mensagens
        chat_container = st.container()

        # Exibir histórico de mensagens dentro do contêiner
        with chat_container:
            for message in st.session_state.massages_fin:
                with st.chat_message(message["role"], avatar=get_user_image_path(message.get("avatar"))):
                    st.markdown(message["content"])

        # Campo de entrada fixo na parte inferior
        prompt = st.chat_input("Digite sua pergunta aqui...", key="chat_input")

        def clear_chat_history():
            st.session_state.massages_fin = [{
                "role": "assistant", "content": 'Olá! Sou o MESTRE BÍBLIA, pronto para ajudá-lo a compreender as '
                                                'análises sobre o financeiro da igreja.'}]

        st.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

        # Processar nova mensagem
        if prompt:
            # Adicionar mensagem do usuário
            st.session_state.massages_fin.append({"role": "user", "content": prompt, "avatar": "user_image_placeholder"})
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
                            st.session_state["claude_model"],
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
                        st.session_state.massages_fin.append({"role": "assistant", "content": clean_response})

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
    st.set_page_config(page_title="Painel Financeiro", page_icon="💰", layout="wide")
    showFinanceiro()  # Chama a função que será responsável pela lógica da página financeira


















































