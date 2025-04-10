# -*- coding: utf-8 -*-
import streamlit as st
import replicate
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import plotly.express as px
from PIL import Image
from datetime import datetime, timedelta, date
import os
import re
from pathlib import Path  # Para manipulação de caminhos de arquivos
from sqlalchemy import (
    create_engine, 
    Column, 
    BigInteger, 
    String, 
    Text, 
    DECIMAL, 
    Integer, 
    Boolean, 
    DateTime, 
    ForeignKey,
    Time,
    Date,
    func,
    text
)
from sqlalchemy import Enum as SQLAlchemyEnum  # Adicione este import
from enum import Enum as PyEnum  # Renomeie para evitar conflito
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError  # Para tratamento de erros
from streamlit_extras.metric_cards import style_metric_cards
from key_config import DATABASE_URL

from sqlalchemy.exc import IntegrityError


# Configuração do banco de dados
engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # Melhor pool management
Base = declarative_base()


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


# Função auxiliar para conversão de data
def to_datetime(data):
    """Converte um objeto datetime.date para datetime.datetime."""
    if isinstance(data, date) and not isinstance(data, datetime):
        return datetime.combine(data, datetime.min.time())  # Converte para datetime
    elif isinstance(data, datetime):
        return data  # Já é um datetime, retorna como está
    else:
        raise TypeError("O argumento 'data' deve ser do tipo datetime.date ou datetime.datetime.")


def salvar_midia(banner, foto_palestrante, nome_evento):
    # Definindo os caminhos para armazenamento
    caminho_eventos = "./src/img/eventos"
    caminho_palestrantes = "./src/img/palestrantes"

    # Criar diretórios se não existirem
    os.makedirs(caminho_eventos, exist_ok=True)
    os.makedirs(caminho_palestrantes, exist_ok=True)

    # Formatar o nome do evento (minúsculas, substituir espaços por hífens)
    nome_evento_formatado = nome_evento.lower().replace(" ", "-")

    # Processar imagem do banner
    banner_path = None
    if banner:
        try:
            # Extrair a extensão do arquivo
            extensao = os.path.splitext(banner.name)[-1].lower()  # Ex: .jpg, .png
            banner_filename = f"{nome_evento_formatado}{extensao}"  # Nome formatado + extensão
            banner_path = os.path.join("eventos", banner_filename)  # Caminho relativo
            caminho_completo = os.path.join(caminho_eventos, banner_filename)  # Caminho completo
            with open(caminho_completo, "wb") as f:
                f.write(banner.getbuffer())  # Salvar o banner
            print(f"Banner salvo em: {caminho_completo}")
        except Exception as e:
            print(f"Erro ao salvar o banner: {e}")

    # Processar imagem do palestrante
    foto_path = None
    if foto_palestrante:
        try:
            # Extrair a extensão do arquivo
            extensao = os.path.splitext(foto_palestrante.name)[-1].lower()  # Ex: .jpg, .png
            foto_filename = f"{nome_evento_formatado}-palestrante{extensao}"  # Nome formatado + sufixo
            foto_path = os.path.join("palestrantes", foto_filename)  # Caminho relativo
            caminho_completo = os.path.join(caminho_palestrantes, foto_filename)  # Caminho completo
            with open(caminho_completo, "wb") as f:
                f.write(foto_palestrante.getbuffer())  # Salvar a foto do palestrante
            print(f"Foto do palestrante salva em: {caminho_completo}")
        except Exception as e:
            print(f"Erro ao salvar a foto do palestrante: {e}")

    return banner_path, foto_path


# Definição de ENUMs para o banco de dados
class TipoEvento(PyEnum):
    gratuito = "Gratuito"
    pago = "Pago"


class StatusEvento(PyEnum):
    agendado = "Agendado"
    cancelado = "Cancelado"
    realizado = "Realizado"


# Definir OraculoUser PRIMEIRO
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

    # Relacionamento com eventos criados
    eventos_criados = relationship("OraculoEvento", back_populates="responsavel")
    eventos_participados = relationship("OraculoEventoParticipantes", back_populates="participante")


# Depois definir OraculoEvento
class OraculoEvento(Base):
    __tablename__ = "oraculo_evento"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome_evento = Column(String(100), nullable=False)
    tema_evento = Column(String(100), nullable=False)
    descricao = Column(Text)
    data_evento = Column(DateTime, nullable=False)
    hora_evento = Column(Time, nullable=False)
    hora_termino = Column(Time, nullable=False)
    local = Column(String(255), nullable=False)
    tipo_evento = Column(String(20), nullable=False)  # Use String se preferir evitar ENUM
    preco = Column(DECIMAL(10, 2))
    max_participantes = Column(Integer)
    palestrante = Column(String(100))
    biografia_palestrante = Column(Text)
    foto_palestrante = Column(String(255))
    contato_email = Column(String(254))
    contato_whatsapp = Column(String(15))
    facebook_url = Column(String(255))
    instagram_url = Column(String(255))
    linkedin_url = Column(String(255))
    banner = Column(String(255))
    responsavel_id = Column(BigInteger, ForeignKey('oraculo_user.id'), nullable=False)
    status = Column(String(20), default="agendado")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    responsavel = relationship("OraculoUser", back_populates="eventos_criados")
    participantes = relationship("OraculoEventoParticipantes", back_populates="evento")


# Modelo para a tabela oraculo_evento_participantes
class OraculoEventoParticipantes(Base):
    __tablename__ = "oraculo_evento_participantes"

    evento_id = Column(BigInteger, ForeignKey('oraculo_evento.id'), primary_key=True)
    usuario_id = Column(BigInteger, ForeignKey('oraculo_user.id'), primary_key=True)
    checkin = Column(Boolean, default=False)
    data_inscricao = Column(DateTime, default=datetime.now)

    # Relacionamentos
    evento = relationship("OraculoEvento", back_populates="participantes")
    participante = relationship("OraculoUser", back_populates="eventos_participados")


# Função para obter dados dos eventos com participantes
def obter_dados_eventos():
    with get_db_session() as session:
        # Query principal com contagem de participantes
        eventos = session.query(
            OraculoEvento,
            func.count(OraculoEventoParticipantes.usuario_id).label("inscritos")
        ).outerjoin(
            OraculoEventoParticipantes
        ).group_by(
            OraculoEvento.id
        ).all()

        # Converter para DataFrame
        dados = []
        for evento, inscritos in eventos:
            dados.append({
                "id": evento.id,
                "nome": evento.nome_evento,
                "tema": evento.tema_evento,
                "data": evento.data_evento,
                "tipo": evento.tipo_evento.value,
                "preco": evento.preco,
                "inscritos": inscritos,
                "status": evento.status.value
            })

        return pd.DataFrame(dados)


# Função para verificar disponibilidade de evento
def verificar_disponibilidade(evento_id):
    evento = get_db_session.get(OraculoEvento, evento_id)
    if not evento.max_participantes:
        return True
    inscritos = get_db_session.query(OraculoEventoParticipantes).filter_by(evento_id=evento_id).count()
    return inscritos < evento.max_participantes


def salvar_evento(
        nome_evento, tema_evento, descricao, data_evento, hora_evento,
        hora_termino, local, tipo_evento, preco, max_participantes,
        palestrante, biografia_palestrante, foto_palestrante,
        contato_email, contato_whatsapp, facebook_url, instagram_url,
        linkedin_url, banner, responsavel_id
):
    try:
        with get_db_session() as session:
            # Verificar evento duplicado
            evento_existente = session.query(OraculoEvento).filter_by(
                nome_evento=nome_evento,
                data_evento=data_evento
            ).first()

            if evento_existente:
                st.error("Evento com mesmo nome e data já cadastrado")
                return False

            # Processar imagem do banner
            if banner:
                banner_path, foto_path = salvar_midia(banner, foto_palestrante)

            else:
                banner_path = None

            novo_evento = OraculoEvento(
                nome_evento=nome_evento,
                tema_evento=tema_evento,
                descricao=descricao,
                data_evento=data_evento,
                hora_evento=hora_evento,
                hora_termino=hora_termino,
                local=local,
                tipo_evento=tipo_evento,
                preco=preco if tipo_evento == "pago" else None,
                max_participantes=max_participantes,
                palestrante=palestrante,
                biografia_palestrante=biografia_palestrante,
                foto_palestrante=foto_palestrante,
                contato_email=contato_email,
                contato_whatsapp=contato_whatsapp,
                facebook_url=facebook_url,
                instagram_url=instagram_url,
                linkedin_url=linkedin_url,
                banner=banner_path,
                responsavel_id=responsavel_id
            )

            session.add(novo_evento)
            session.commit()
            return True
    except IntegrityError as e:
        session.rollback()
        st.error(f"Erro de integridade: {str(e)}")
        return False
    except Exception as e:
        session.rollback()
        st.error(f"Erro inesperado: {str(e)}")
        return False


def inscrever_participante(evento_id, usuario_id):
    try:
        with get_db_session() as session:
            # Verificar disponibilidade
            if not verificar_disponibilidade(evento_id):
                st.error("Limite de participantes atingido")
                return False

            # Verificar se já está inscrito
            inscricao_existente = session.query(OraculoEventoParticipantes).filter_by(
                evento_id=evento_id,
                usuario_id=usuario_id
            ).first()

            if inscricao_existente:
                st.warning("Usuário já inscrito neste evento")
                return False

            nova_inscricao = OraculoEventoParticipantes(
                evento_id=evento_id,
                usuario_id=usuario_id,
                checkin=False
            )

            session.add(nova_inscricao)
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        st.error(f"Erro na inscrição: {str(e)}")
        return False


def verificar_disponibilidade(evento_id):
    with get_db_session() as session:
        evento = session.get(OraculoEvento, evento_id)
        if not evento.max_participantes:
            return True
        inscritos = session.query(OraculoEventoParticipantes).filter_by(
            evento_id=evento_id
        ).count()
        return inscritos < evento.max_participantes


def atualizar_evento(evento_id, dados_atualizados):
    try:
        with get_db_session() as session:
            evento = session.get(OraculoEvento, evento_id)
            if not evento:
                st.error("Evento não encontrado")
                return False

            # Atualizar campos permitidos
            for campo, valor in dados_atualizados.items():
                if campo == 'banner' and valor:
                    # Remover banner antigo
                    if evento.banner and os.path.exists(evento.banner):
                        os.remove(evento.banner)

                    # Salvar novo banner
                    banner_path = None
                    try:
                        # Garante formatação correta e salva o novo banner
                        banner_path = salvar_midia(valor, None)[0]  # Apenas o banner é salvo
                    except Exception as e:
                        st.error(f"Falha ao processar banner: {str(e)}")
                        return

                    setattr(evento, campo, banner_path)
                else:
                    setattr(evento, campo, valor)

            session.commit()
            return True
    except Exception as e:
        session.rollback()
        st.error(f"Erro na atualização: {str(e)}")
        return False


def deletar_evento(evento_id):
    try:
        with get_db_session() as session:
            evento = session.get(OraculoEvento, evento_id)
            if not evento:
                st.error("Evento não encontrado")
                return False

            # Remover banner
            if evento.banner and os.path.exists(evento.banner):
                os.remove(evento.banner)

            # Remover inscrições
            session.query(OraculoEventoParticipantes).filter_by(
                evento_id=evento_id
            ).delete()

            session.delete(evento)
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        st.error(f"Erro na exclusão: {str(e)}")
        return False


def listar_eventos(usuario_id=None, status=None):
    try:
        with get_db_session() as session:
            query = session.query(
                OraculoEvento,
                func.count(OraculoEventoParticipantes.usuario_id).label("inscritos")
            ).outerjoin(
                OraculoEventoParticipantes
            ).group_by(
                OraculoEvento.id
            )

            if usuario_id:
                query = query.filter(OraculoEvento.responsavel_id == usuario_id)
            if status:
                query = query.filter(OraculoEvento.status == status)

            eventos = query.all()

            return [{
                "id": e.id,
                "nome": e.nome_evento,
                "data": e.data_evento.strftime("%d/%m/%Y %H:%M") if e.data_evento else "Data não definida",
                "tipo": e.tipo_evento,  # Removido .value
                "preco": float(e.preco) if e.preco else 0.0,
                "inscritos": inscritos,
                "status": e.status,  # Removido .value
                "banner": e.banner,
                "facebook_url": e.facebook_url,
                "instagram_url": e.instagram_url,
                "linkedin_url": e.linkedin_url
            } for e, inscritos in eventos]
    except Exception as e:
        st.error(f"Erro ao listar eventos: {str(e)}")
        return []


def create_calendar(eventos):
    """Cria um calendário interativo com eventos.

    Args:
        eventos: Lista de dicionários com chaves 'Event', 'Start', 'End', 'Tipo', 'ID'

    Returns:
        fig: Objeto Figure do Plotly
    """
    # Converter para DataFrame
    df = pd.DataFrame(eventos)

    # Mapear cores por tipo de evento
    color_map = {
        "gratuito": "#3CB371",
        "pago": "#DC143C"
    }

    # Criar gráfico de calendário
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y=[""] * len(df),  # Garante visualização horizontal
        title="",
        text="Event",
        color="Tipo",
        color_discrete_map=color_map,
        hover_data=["ID"],
        labels={"Tipo": "Tipo de Evento"}
    )

    # Configurações visuais
    fig.update_layout(
        title_x=0.5,
        xaxis_title="",
        yaxis_title="",
        showlegend=True,
        legend_title="Legenda",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        height=600
    )

    # Ajustes específicos para visualização de calendário
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1 semana", step="day", stepmode="backward"),
                dict(count=1, label="1 mês", step="month", stepmode="backward"),
                dict(step="all", label="Tudo")
            ])
        ),
        rangeslider_visible=False
    )

    # Adicionar tooltips personalizados
    fig.update_traces(
        hovertemplate=
        "<b>%{text}</b><br>" +
        "Data: %{x|%d/%m/%Y %H:%M}<br>" +
        "Tipo: %{customdata[0]}<br>" +
        "ID: %{customdata[1]}"
    )

    return fig


def obter_pastores():
    """Retorna lista de pastores (id, nome) do banco de dados"""
    with get_db_session() as session:
        query = text("""
            SELECT u.id, u.name 
            FROM oraculo_user u
            JOIN oraculo_cargo c ON u.cargo_id = c.id
            WHERE c.name = 'Pastor'
            AND u.deleted_at IS NULL
        """)
        result = session.execute(query).fetchall()
        return {nome: id for id, nome in result}  # Dicionário {Nome: ID}


# Função para obter o caminho completo da imagem do usuário
def get_user_image_path(user_image):
    """
    Retorna o caminho completo da imagem do usuário.
    Se a imagem não existir, retorna um caminho padrão.
    """
    if user_image:
        image_path = os.path.join("./media/src/img/eventos", user_image)
        if os.path.exists(image_path):
            return image_path

def show_evento():

    # Inicializa estado da sessão
    if "eventos" not in st.session_state:
        st.session_state.eventos = []

    # 📅 **Interface Principal**
    st.title("📅 Gestão de Eventos Recomeçar")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Novo Evento",
        "📋 Listar Eventos",
        "📝 Inscrições",
        "📊 Relatórios",
        "📈 Análise Inteligente"
    ])

    st.divider()

    # 📅 **Aba de Cadastro de Evento**
    with tab1:
        st.expander("📅 Cadastrar Novo Evento")
        with st.form("form_cadastro_evento", clear_on_submit=True, border=True):

            st.header("🗓️ Calendário de Eventos")

            # Obter eventos do banco
            eventos = listar_eventos(status="agendado")
            if not eventos:
                st.info("Nenhum evento agendado")
            else:
                # Converter para formato adequado ao calendário
                eventos_cal = []
                for evento in eventos:
                    # Certifique-se de que evento["data"] é um objeto datetime
                    data_evento = datetime.strptime(evento["data"],
                                                    "%d/%m/%Y %H:%M")  # Ajuste o formato conforme necessário
                    eventos_cal.append({
                        "Event": evento["nome"],
                        "Start": data_evento,
                        "End": data_evento + timedelta(hours=2),  # Ajustar conforme duração real
                        "Tipo": evento["tipo"],
                        "ID": evento["id"]
                    })

                # Criar calendário interativo
                fig = create_calendar(eventos_cal)
                st.plotly_chart(fig, use_container_width=True)

                # Container para detalhes do evento
                detalhes_container = st.empty()
                inscricao_container = st.empty()

                # Callback para seleção de evento
                def on_event_click(trace, points, state):
                    if points.point_inds:
                        evento_selecionado = eventos[points.point_inds[0]]
                        with detalhes_container.container():
                            st.subheader(evento_selecionado["nome"])
                            st.write(f"**Tema:** {evento_selecionado['tema']}")
                            st.write(f"**Data:** {evento_selecionado['data'].strftime('%d/%m/%Y %H:%M')}")
                            st.write(f"**Local:** {evento_selecionado['local']}")
                            st.write(
                                f"**Vagas:** {evento_selecionado['max_participantes'] - evento_selecionado['inscritos']} restantes")

                            # Botão de inscrição
                            usuario_id = st.number_input("Seu ID", min_value=1, step=1, key="cal_inscricao")
                            if st.button("✅ Inscrever-se", key="btn_inscricao"):
                                if inscrever_participante(evento_selecionado["id"], usuario_id):
                                    st.success("Inscrição realizada!")
                                else:
                                    st.error("Falha na inscrição")

                # Adicionar interatividade ao calendário
                fig.data[0].on_click(on_event_click)

            # Informações básicas
            col1, col2 = st.columns(2)
            with col1:
                nome_evento = st.text_input("Nome do Evento*", "")
                tema_evento = st.text_input("Tema do Evento*", "")
                data_evento = st.date_input("Data do Evento*")
                hora_evento = st.time_input("Hora de Início*")
                hora_termino = st.time_input("Hora de Término*")
                descricao = st.text_area("Sobre o Evento:")

            with col2:
                local = st.text_input("Local do Evento*", "")
                tipo_evento = st.selectbox("Tipo de Evento*", ["Gratuito", "Pago", "Beneficente"])

                # Campo de preço condicional
                if tipo_evento == "Pago":
                    st.info("⚠️ Para criar um evento pago, crie um link de pagamento antes de salvar o evento.")

                    # Campo para inserir o link de pagamento
                    link_pagamento = st.chat_input("Insira a URL do link de pagamento criado:")

                    # Verifica se o link foi inserido
                    if link_pagamento:
                        st.success("Link de pagamento recebido.")
                        preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)
                    else:
                        st.warning("⚠️ Por favor, insira o link de pagamento antes de continuar.")
                elif tipo_evento == "Beneficente":
                    st.info(
                        "📚 Este é um evento beneficente. Os participantes devem levar 1 kg de alimento não perecível.")
                    preco = 0.0  # Define o preço como 0 para eventos beneficentes
                elif tipo_evento == "Gratuito":
                    preco = 0.0  # Define o preço como 0 para eventos gratuitos

                max_participantes = st.number_input("Limite de Participantes", min_value=0)

                # Processar banner
                banner = st.file_uploader(
                    "Banner do Evento",
                    type=["jpg", "jpeg", "png"],
                    key="banner_uploader"  # Chave única obrigatória
                )

                # Inicializar banner_path como None
                banner_path = None
                if banner:
                    st.image(banner, caption="Visualizar Banner", use_container_width=True)
                    try:
                        # Salvar o banner usando a função salvar_midia
                        banner_path, _ = salvar_midia(banner, None)  # Apenas o banner é salvo
                        if banner_path:
                            st.success(f"Banner salvo em: {banner_path}")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {str(e)}")

            # Informações do palestrante
            with st.expander("🎤 Dados do Palestrante"):
                palestrante = st.text_input("Nome do Palestrante")
                biografia_palestrante = st.text_area("Biografia")
                foto_palestrante = st.file_uploader("Foto do Palestrante", type=["jpg", "png"])

            # Contatos
            with st.expander("📞 Informações de Contato"):
                contato_email = st.text_input("E-mail para Contato")
                contato_whatsapp = st.text_input(
                    "WhatsApp (xx9xxxxxxxx)",
                    placeholder="31987654321",
                    max_chars=15,
                    help="Apenas números, sem espaços ou caracteres especiais"
                )

                facebook_url = st.text_input("Facebook URL")
                instagram_url = st.text_input("Instagram URL")
                linkedin_url = st.text_input("LinkedIn URL")

            # Responsável
            with st.expander("👤 Responsável Pelo Evento"):
                # Obter lista de pastores
                pastores = obter_pastores()

                if not pastores:
                    st.warning("⚠️ Nenhum pastor cadastrado")
                    responsavel_id = None
                else:
                    # Selectbox com nomes
                    nome_responsavel = st.selectbox(
                        "Selecione o Pastor Responsável*",
                        options=list(pastores.keys()),
                        index=None,
                        placeholder="Escolha um pastor..."
                    )

                    # Obter ID correspondente
                    responsavel_id = pastores.get(nome_responsavel) if nome_responsavel else None

            # Botão de envio
            submitted = st.form_submit_button("✅ Criar Evento")
            if submitted:
                if contato_whatsapp:
                    contato_whatsapp = re.sub(r'\D', '', contato_whatsapp)
                    if len(contato_whatsapp) > 15:
                        st.error("⚠️ WhatsApp excede o limite de 15 dígitos")
                # Validações
                if not all([nome_evento, tema_evento, data_evento, hora_evento, local]):
                    st.error("⚠️ Preencha todos os campos obrigatórios (*)")
                    return

                # Salvar evento
                sucesso = salvar_evento(
                    nome_evento=nome_evento,
                    tema_evento=tema_evento,
                    descricao=descricao,
                    data_evento=datetime.combine(data_evento, hora_evento),
                    hora_evento=hora_evento,
                    hora_termino=hora_termino,
                    local=local,
                    tipo_evento=tipo_evento,
                    preco=preco if tipo_evento == "pago" else None,
                    max_participantes=max_participantes,
                    palestrante=palestrante,
                    biografia_palestrante=biografia_palestrante,
                    foto_palestrante=foto_palestrante.name if foto_palestrante else None,
                    contato_email=contato_email,
                    contato_whatsapp=contato_whatsapp,
                    facebook_url=facebook_url,
                    instagram_url=instagram_url,
                    linkedin_url=linkedin_url,
                    banner=banner_path,  # banner_path agora sempre tem um valor (None ou caminho válido)
                    responsavel_id=responsavel_id
                )

                if sucesso:
                    st.success(f"🎉 Evento '{nome_evento}' criado com sucesso!")
                    st.balloons()
                else:
                    st.error("⚠️ Falha ao criar evento")

    # 📋 **Aba de Listagem de Eventos**
    with tab2:
        st.header("📋 Eventos Cadastrados")
        eventos = listar_eventos()

        if not eventos:
            st.info("Nenhum evento cadastrado")
        else:
            # Dividir os eventos em grupos de 3 por linha
            num_eventos = len(eventos)
            num_rows = (num_eventos + 2) // 3  # Calcula o número de linhas necessárias

            for row in range(num_rows):
                # Criar uma linha com 3 colunas
                cols = st.columns(3)

                for i in range(3):
                    event_index = row * 3 + i  # Índice do evento na lista
                    if event_index < num_eventos:  # Verifica se ainda há eventos para exibir
                        evento = eventos[event_index]

                        with cols[i].container():
                            # Coluna de imagem
                            caminho_eventos = "./src/img/eventos"  # Caminho onde os banners são armazenados
                            banner_path = evento.get('banner')  # Supondo que 'banner' contém o nome do arquivo

                            if banner_path:  # Verifica se banner_path não é None
                                caminho_completo = os.path.join(caminho_eventos,
                                                                banner_path)  # Monta o caminho completo
                                if os.path.exists(caminho_completo):
                                    st.image(caminho_completo, width=150)
                                else:
                                    st.write("❌ Sem banner ou arquivo não encontrado")
                            else:
                                st.write("❌ Nenhum banner foi carregado.")

                            # Informações principais
                            st.subheader(f"📅 {evento['nome']}")
                            st.caption(f"ID: {evento['id']}")

                            st.markdown(f"""
                                **📅 Data:** {evento['data']}  
                                **⏰ Tipo:** {evento['tipo'].capitalize()}  
                                **👥 Inscritos:** {evento['inscritos']}  
                                **💰 Preço:** {evento['preco'] if evento['preco'] else 'Gratuito'}  
                                **📌 Status:** {evento['status'].capitalize()}
                            """)

                            # Links das redes sociais
                            if evento['facebook_url']:
                                st.markdown(f"[Facebook]({evento['facebook_url']})", unsafe_allow_html=True)
                            if evento['instagram_url']:
                                st.markdown(f"[Instagram]({evento['instagram_url']})", unsafe_allow_html=True)
                            if evento['linkedin_url']:
                                st.markdown(f"[LinkedIn]({evento['linkedin_url']})", unsafe_allow_html=True)

                            st.divider()

    # 📝 **Aba de Inscrições**
    with tab3:
        st.header("📝 Inscrição em Eventos")
        evento_id = st.number_input("ID do Evento", min_value=1, step=1)
        usuario_id = st.number_input("Seu ID de Membro", min_value=1, step=1)

        if st.button("✅ Realizar Inscrição"):
            if inscrever_participante(evento_id, usuario_id):
                st.success("Inscrição realizada com sucesso!")
            else:
                st.error("Falha na inscrição")

    # 📊 **Aba de Relatórios**
    with tab4:
        st.header("📊 Relatórios de Eventos")

        # Usar sessão dentro de contexto seguro
        with get_db_session() as session:  # <--- Correção principal
            # 📊 **Seção de Métricas em Tempo Real**
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_eventos = len(listar_eventos())
                st.metric(label="📅 Total de Eventos", value=total_eventos)

            with col2:
                eventos_ativos = len(listar_eventos(status="agendado"))
                st.metric(label="⏳ Eventos Ativos", value=eventos_ativos)

            with col3:
                participantes_mes = session.query(
                    func.count(OraculoEventoParticipantes.usuario_id)
                ).join(
                    OraculoEvento
                ).filter(
                    OraculoEvento.data_evento >= datetime.now().replace(day=1)
                ).scalar() or 0  # Adicionado fallback para 0
                st.metric(label="👥 Participantes/Mês", value=participantes_mes)

            with col4:
                eventos_alerta = session.query(OraculoEvento).filter(
                    OraculoEvento.data_evento <= datetime.now() + timedelta(days=2),
                    OraculoEvento.status == "agendado"
                ).count()
                st.metric(label="⚠️ Eventos Urgentes", value=eventos_alerta)

            # 🚨 **Seção de Alertas**
            st.subheader("🚨 Alertas Críticos")
            eventos_proximos = session.query(OraculoEvento).filter(
                OraculoEvento.data_evento.between(
                    datetime.now(),
                    datetime.now() + timedelta(days=7)
                ),
                OraculoEvento.status == "agendado"
            ).all()

            if not eventos_proximos:
                st.info("Nenhum evento próximo nos próximos 7 dias")
            else:
                for evento in eventos_proximos:
                    # Garantir que data_evento seja tratada como datetime.datetime
                    data_evento = to_datetime(evento.data_evento)

                    # Calcular os dias restantes
                    dias_restantes = (data_evento - datetime.now()).days

                    # Definir a cor com base nos dias restantes
                    cor = "red" if dias_restantes <= 2 else "orange"

                    # Calcular as vagas restantes
                    vagas_restantes = evento.max_participantes - len(evento.participantes)

                    # Exibir o evento formatado
                    st.markdown(f"""
                            <div style='border: 2px solid {cor}; border-radius: 10px; padding: 10px; margin: 5px 0'>
                                <h4>{evento.nome_evento}</h4>
                                <p>Data: {data_evento.strftime('%d/%m/%Y %H:%M')}</p>
                                <p>Vagas restantes: {vagas_restantes}</p>
                            </div>
                        """, unsafe_allow_html=True)

            # ✅ **Seção de Check-in**
            st.subheader("✅ Controle de Presença")
            with st.form("form_checkin"):
                evento_id = st.number_input("ID do Evento", min_value=1, step=1)
                usuario_id = st.number_input("ID do Participante", min_value=1, step=1)

                if st.form_submit_button("Registrar Check-in"):
                    try:
                        with get_db_session() as checkin_session:  # Nova sessão para operação
                            registro = checkin_session.query(OraculoEventoParticipantes).filter_by(
                                evento_id=evento_id,
                                usuario_id=usuario_id
                            ).first()

                            if not registro:
                                st.error("Participante não inscrito neste evento")
                            else:
                                registro.checkin = True
                                checkin_session.commit()
                                st.success("Check-in registrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")

            # 📄 **Seção de Relatórios**
            st.subheader("📄 Exportar Relatórios")
            tipo_relatorio = st.selectbox("Tipo de Relatório", ["Completo", "Check-ins", "Financeiro"])

            if st.button("Gerar Relatório"):
                try:
                    with get_db_session() as report_session:  # Sessão dedicada para relatórios
                        if tipo_relatorio == "Completo":
                            df = pd.DataFrame(listar_eventos())
                            df.to_excel("relatorio_completo.xlsx", index=False)
                            st.success("Relatório completo gerado!")

                        elif tipo_relatorio == "Check-ins":
                            query = report_session.query(
                                OraculoEvento.nome_evento,
                                OraculoUser.name,
                                OraculoEventoParticipantes.checkin
                            ).join(
                                OraculoEventoParticipantes, OraculoEvento.id == OraculoEventoParticipantes.evento_id
                            ).join(
                                OraculoUser, OraculoEventoParticipantes.usuario_id == OraculoUser.id
                            )
                            df = pd.read_sql(query.statement, report_session.bind)
                            df.to_excel("relatorio_checkins.xlsx", index=False)
                            st.success("Relatório de check-ins gerado!")

                        elif tipo_relatorio == "Financeiro":
                            eventos_pagos = report_session.query(OraculoEvento).filter_by(tipo_evento="pago").all()
                            dados = [{
                                "Evento": evento.nome_evento,
                                "Inscritos": len(evento.participantes),
                                "Receita": evento.preco * len(evento.participantes)
                            } for evento in eventos_pagos]
                            pd.DataFrame(dados).to_excel("relatorio_financeiro.xlsx", index=False)
                            st.success("Relatório financeiro gerado!")
                except Exception as e:
                    st.error(f"Erro ao gerar relatório: {str(e)}")

    # 📈 **Aba de Análise Inteligente**
    with tab5:
        st.header("📈 Análise Inteligente")
        st.subheader("📖 Narrativa Gerada Automaticamente")

        # Carregar dados dos eventos
        with get_db_session() as session:
            eventos = session.query(OraculoEvento).all()

            # Formatar dados para a LLM
            dados_llm = []
            for evento in eventos:
                dados_llm.append(f"""
                    Evento: {evento.nome_evento}
                    Tema: {evento.tema_evento}
                    Data: {evento.data_evento.strftime('%d/%m/%Y')}
                    Horário: {evento.hora_evento} - {evento.hora_termino}
                    Tipo: {evento.tipo_evento}
                    Preço: R$ {evento.preco} (Gratuito se 0)
                    Palestrante: {evento.palestrante}
                    Vagas: {evento.max_participantes}
                """)
            dados_formatados = "\n\n".join(dados_llm) if dados_llm else "Nenhum evento cadastrado"

        # Sistema de prompt com dados dinâmicos
        system_prompt = f'''
        Você é MESTRE BÍBLIA, especialista em análise de eventos cristãos.
        Suas respostas devem ser diretas e focadas em análise dos dados fornecidos sobre eventos.

        Regras:
        1. Cumprimentando o usuário da mesma forma que ele te cumprimentou (ex: "Bom dia", "Olá").
        2. Após o cumprimento, pergunte diretamente: "O que você gostaria de analisar hoje?".
        3. Seu cumprimento será somente na primeira interação com o usuário para não ficar repetitivo.
        4. Use os dados abaixo APENAS quando necessário para responder perguntas específicas do usuário.
        5. Não liste todos os eventos disponíveis automaticamente, a menos que o usuário peça.
        6. Para perguntas sobre finanças, calcule receitas automaticamente.

        Dados dos Eventos:
        {dados_formatados}
        '''

        # Set a default model
        if "deepseek_model" not in st.session_state:
            st.session_state["deepseek_model"] = "deepseek-ai/deepseek-r1"

        # Interface do chat
        if "massages_eve" not in st.session_state:
            st.session_state.massages_eve = []

        # Contêiner para o histórico de mensagens
        chat_container = st.container()

        # Exibir histórico de mensagens dentro do contêiner
        with chat_container:
            for message in st.session_state.massages_eve:
                with st.chat_message(message["role"], avatar=get_user_image_path(message.get("avatar"))):
                    st.markdown(message["content"])

        # Campo de entrada fixo na parte inferior
        prompt = st.chat_input("Digite sua pergunta aqui...", key="chat_input")

        def clear_chat_history():
            st.session_state.massages_fin = [{
                "role": "assistant", "content": 'Olá! Sou o MESTRE BÍBLIA, pronto para ajudá-lo a compreender as '
                                                'análises sobre os eventos da igreja.'}]

        st.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

        # Processar nova mensagem
        if prompt:
            # Adicionar mensagem do usuário
            st.session_state.massages_eve.append({"role": "user", "content": prompt, "avatar": "user_image_placeholder"})
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
                                clean_response = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()
                                response_container.markdown(clean_response)

                        # Salvar a resposta completa no histórico
                        st.session_state.massages_eve.append({"role": "assistant", "content": clean_response})

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
    st.set_page_config(page_title="Oráculo Bíblia", page_icon="⛪", layout="wide")
    show_evento()