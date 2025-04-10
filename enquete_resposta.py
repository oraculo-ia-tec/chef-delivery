import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List
import requests
import pandas as pd
from key_config import DATABASE_URL, URL_DJANGO_ENQUETE, TOKEN_API_DJANGO, URL_TOKEN_API
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, text, func
from sqlalchemy.orm import sessionmaker, declarative_base
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# Definição da tabela Enquete
class Enquete(Base):
    __tablename__ = "enquete_enquete"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(String, nullable=False)
    data_inicio = Column(DateTime, default=datetime.utcnow)
    data_fim = Column(DateTime, nullable=False)
    ativo = Column(Boolean, default=True)
    opcao1 = Column(String(200))
    opcao2 = Column(String(200))
    opcao3 = Column(String(200))
    opcao4 = Column(String(200))
    created_dt = Column(DateTime, default=datetime.utcnow)
    updated_dt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("oraculo_user.id"))
    cargo_id = Column(Integer, ForeignKey("oraculo_user.id"))  # Nova coluna para o cargo


def verificar_usuario(username: str, password: str) -> Optional[Dict]:
    """Verifica credenciais do usuário no banco de dados."""
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT username, password, cargo_id 
                FROM oraculo_user 
                WHERE username = :username
            """)
            result = connection.execute(query, {"username": username}).fetchone()

            if result:
                return {'username': result[0], 'cargo_id': result[2]}
        return None
    except Exception as e:
        st.error(f"Erro ao verificar usuário: {str(e)}")
        return None


def obter_cargos() -> List[str]:
    """Obtém os nomes de todos os cargos disponíveis."""
    try:
        with engine.connect() as connection:
            query = text("SELECT name FROM oraculo_cargo")
            cargos = connection.execute(query).fetchall()
            return [cargo[0] for cargo in cargos]
    except Exception as e:
        st.error(f"Erro ao buscar os cargos: {str(e)}")
        return []


def obter_enquetes() -> List[Dict]:
    """Recupera todas as enquetes cadastradas no banco de dados."""
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT e.id, e.titulo, e.descricao, e.data_inicio, e.data_fim, e.ativo 
                FROM enquete_enquete e
                ORDER BY e.created_dt DESC
            """)
            enquetes = connection.execute(query).fetchall()

            resultado = []
            for e in enquetes:
                enquete_id = e[0]

                # Buscar os nomes dos cargos direcionados
                query_cargos = text("""
                    SELECT c.name 
                    FROM enquete_enquete_direcionado_a ed
                    JOIN oraculo_cargo c ON ed.cargo_id = c.id
                    WHERE ed.enquete_id = :enquete_id
                """)
                cargos = connection.execute(query_cargos, {"enquete_id": enquete_id}).fetchall()
                cargos_nomes = [cargo[0] for cargo in cargos]

                resultado.append({
                    'ID': enquete_id,
                    'Título': e[1],
                    'Descrição': e[2],
                    'Data de Início': e[3].strftime('%d/%m/%Y %H:%M:%S'),
                    'Data de Fim': e[4].strftime('%d/%m/%Y %H:%M:%S'),
                    'Ativo': 'Sim' if e[5] else 'Não',
                    'Direcionado a': ", ".join(cargos_nomes) if cargos_nomes else "Nenhum"
                })

            return resultado
    except Exception as e:
        st.error(f"Erro ao buscar enquetes: {str(e)}")
        return []


def validate_poll_dates(data_inicio: datetime, data_fim: datetime) -> bool:
    """Valida as datas da enquete."""
    now = datetime.now()
    if data_inicio < now:
        st.error("A data de início não pode ser anterior à data atual.")
        return False
    if data_fim <= data_inicio:
        st.error("A data de fim deve ser posterior à data de início.")
        return False
    return True


def salvar_enquete(titulo, descricao, data_inicio, data_fim, ativo, opcoes, cargos_selecionados, usuario_id):
    try:
        with engine.connect() as connection:
            # Converter datas para datetime.datetime, se necessário
            if isinstance(data_inicio, str):
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S")
            if isinstance(data_fim, str):
                data_fim = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")

            # Inserir a enquete na tabela enquete_enquete
            query_enquete = text("""
                INSERT INTO enquete_enquete (
                    titulo, descricao, data_inicio, data_fim, ativo, opcao1, opcao2, opcao3, opcao4, created_dt, updated_dt, usuario_id
                )
                VALUES (
                    :titulo, :descricao, :data_inicio, :data_fim, :ativo, :opcao1, :opcao2, :opcao3, :opcao4, :created_dt, :updated_dt
                )
            """)
            result = connection.execute(
                query_enquete,
                {
                    "titulo": titulo.strip(),
                    "descricao": descricao.strip(),
                    "data_inicio": data_inicio.strftime("%Y-%m-%d %H:%M:%S"),
                    "data_fim": data_fim.strftime("%Y-%m-%d %H:%M:%S"),
                    "ativo": ativo,
                    "opcao1": opcoes[0].strip(),
                    "opcao2": opcoes[1].strip(),
                    "opcao3": opcoes[2].strip(),
                    "opcao4": opcoes[3].strip(),
                    "created_dt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_dt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            enquete_id = result.lastrowid  # Obtém o ID da enquete inserida

            # Inserir o relacionamento entre enquete e cargos na tabela enquete_enquete_direcionado_a
            for cargo_id in cargos_selecionados:
                query_relacionamento = text("""
                    INSERT INTO enquete_enquete_direcionado_a (enquete_id, cargo_id)
                    VALUES (:enquete_id, :cargo_id)
                """)
                connection.execute(query_relacionamento, {"enquete_id": enquete_id, "cargo_id": cargo_id})

            connection.commit()
            return True
    except Exception as e:
        print(f"Erro ao salvar enquete: {e}")
        return False


def obter_nomes_cargos() -> Dict[str, int]:
    """Busca todos os nomes de cargos cadastrados e seus IDs."""
    try:
        with engine.connect() as connection:
            query = text("SELECT id, name FROM oraculo_cargo")
            result = connection.execute(query).fetchall()

            if not result:
                st.warning("⚠️ Nenhum cargo encontrado no banco de dados.")
                return {}

            return {cargo[1]: cargo[0] for cargo in result}  # Retorna um dicionário {nome: id}
    except Exception as e:
        st.error(f"Erro ao buscar nomes de cargos: {str(e)}")
        return {}


def criar_enquete():
    # Interface do Streamlit
    st.title("📊 Sistema de Enquetes")
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Cadastrar",
        "📋 Listar",
        "🗳️ Editar ou Excluir Enquetes",
        "📈 Estatísticas"
    ])

    # Aba de Cadastro de Enquetes
    with tab1:
        st.header("Criar Nova Enquete")

        # Formulário para adicionar uma nova enquete
        with st.form("form_cadastro_enquete", clear_on_submit=True, border=True):
            st.subheader("Nova Enquete")

            # Layout em duas colunas
            col1, col2 = st.columns(2)
            with col1:
                titulo = st.text_input("Título da Enquete", placeholder="Digite o título da enquete")
                descricao = st.text_area("Descrição", placeholder="Descreva a enquete")
                data_inicio = st.date_input("Data de Início", min_value=datetime.today())
                opcao1 = st.text_input("Opção 1", placeholder="Digite a primeira opção")
            with col2:
                ativo = st.radio("Status da Enquete", ["Ativa", "Inativa"])
                ativo = 1 if ativo == "Ativa" else 0
                data_fim = st.date_input("Data de Término", min_value=datetime.today())
                opcao2 = st.text_input("Opção 2", placeholder="Digite a segunda opção")
                opcao3 = st.text_input("Opção 3", placeholder="Digite a terceira opção")
                opcao4 = st.text_input("Opção 4", placeholder="Digite a quarta opção")

            # Selecionar cargos para direcionar a enquete
            nomes_cargos = obter_nomes_cargos()
            cargos_selecionados = st.multiselect("Direcionar Enquete Para:", list(nomes_cargos.keys()))

            # Botão para enviar o formulário
            if st.form_submit_button("✅ Criar Enquete"):
                if not all([titulo.strip(), descricao.strip(), opcao1.strip(), opcao2.strip(), opcao3.strip(),
                            opcao4.strip()]):
                    st.error("⚠️ Preencha todos os campos obrigatórios.")
                elif not cargos_selecionados:
                    st.error("⚠️ Selecione pelo menos um cargo para direcionar a enquete.")
                else:
                    # Converter datas para datetime.datetime
                    data_inicio = datetime.combine(data_inicio, datetime.min.time())
                    data_fim = datetime.combine(data_fim, datetime.min.time())

                    # Salvar a enquete no banco de dados
                    sucesso = salvar_enquete(
                        titulo=titulo.strip(),
                        descricao=descricao.strip(),
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        ativo=ativo,
                        opcoes=[opcao1.strip(), opcao2.strip(), opcao3.strip(), opcao4.strip()],
                        cargos_selecionados=[nomes_cargos[cargo] for cargo in cargos_selecionados],
                    )
                    if sucesso:
                        st.success("🎉 Enquete criada com sucesso!")
                    else:
                        st.error("⚠️ Falha ao criar a enquete. Verifique os dados e tente novamente.")

    # Aba para Listar Enquetes
    with tab2:
        st.header("📋 Lista de Enquetes Ativas")

        # Barra de Pesquisa: Filtrar por 3 primeiras letras do título
        search_query = st.text_input("🔍 Pesquisar Enquetes (Digite as 3 primeiras letras)", "")
        if search_query and len(search_query) < 3:
            st.warning("⚠️ Digite pelo menos 3 letras para pesquisar.")
        else:
            # Obter enquetes ativas do banco de dados
            with Session() as session:
                query = session.query(Enquete).filter_by(ativo=True)

                # Aplicar filtro se houver uma pesquisa válida
                if search_query and len(search_query) >= 3:
                    query = query.filter(Enquete.titulo.ilike(f"{search_query}%"))

                enquetes = query.all()

                # Verificar se há enquetes disponíveis
                if not enquetes:
                    st.info("ℹ️ Nenhuma enquete ativa encontrada.")
                else:
                    # Exibir cada enquete em um expander
                    for enquete in enquetes:
                        with st.expander(f"📌 {enquete.titulo}"):
                            st.write(f"**Descrição:** {enquete.descricao}")
                            st.write(f"**Expira em:** {enquete.data_fim.strftime('%d/%m/%Y %H:%M:%S')}")
                            st.write(
                                f"**Opções:** {enquete.opcao1}, {enquete.opcao2}, {enquete.opcao3}, {enquete.opcao4}")

    # ✏️ **Aba de Edição/Exclusão de Enquetes**
    with tab3:
        st.header("🗳️ Editar ou Excluir Enquetes")

        # Carregar as enquetes do banco de dados
        with Session() as session:
            enquetes = session.query(Enquete).all()

        if not enquetes:
            st.warning("⚠️ Nenhuma enquete cadastrada.")
        else:
            # Lista de títulos das enquetes para seleção
            enquetes_titulos = [enquete.titulo for enquete in enquetes]
            enquete_selecionada = st.selectbox("Escolha a enquete:", enquetes_titulos, key="enquete_editar")

            # Busca a enquete selecionada no banco de dados
            enquete_atual = next((e for e in enquetes if e.titulo == enquete_selecionada), None)

            if enquete_atual:
                # Modo de Edição
                st.subheader(f"Editar: {enquete_atual.titulo}")

                with st.form("editar_enquete", border=True):
                    novo_titulo = st.text_input("Título da Enquete", enquete_atual.titulo, key="novo_titulo")
                    nova_descricao = st.text_area("Descrição", enquete_atual.descricao, key="nova_descricao")
                    nova_data_fim = st.date_input("📅 Data de Expiração", value=enquete_atual.data_fim,
                                                  key="nova_data_fim")

                    col1, col2 = st.columns(2)  # Dividir campos em duas colunas

                    with col1:
                        nova_opcao1 = st.text_input("Opção 1", enquete_atual.opcao1, key="nova_opcao1")
                        nova_opcao2 = st.text_input("Opção 2", enquete_atual.opcao2, key="nova_opcao2")

                    with col2:
                        nova_opcao3 = st.text_input("Opção 3", enquete_atual.opcao3, key="nova_opcao3")
                        nova_opcao4 = st.text_input("Opção 4", enquete_atual.opcao4, key="nova_opcao4")

                    # Botão para salvar alterações
                    submit_button = st.form_submit_button("💾 Salvar Alterações")

                    if submit_button:
                        try:
                            # Validação dos campos
                            if not novo_titulo.strip() or not nova_descricao.strip() or not all(
                                    [nova_opcao1, nova_opcao2, nova_opcao3, nova_opcao4]):
                                st.error("⚠️ Preencha todos os campos obrigatórios.")
                            elif nova_data_fim < datetime.now().date():
                                st.error("⚠️ A data de expiração não pode ser anterior à data atual.")
                            else:
                                # Atualizar dados no banco de dados
                                enquete_atual.titulo = novo_titulo.strip()
                                enquete_atual.descricao = nova_descricao.strip()
                                enquete_atual.data_fim = nova_data_fim
                                enquete_atual.opcao1 = nova_opcao1.strip()
                                enquete_atual.opcao2 = nova_opcao2.strip()
                                enquete_atual.opcao3 = nova_opcao3.strip()
                                enquete_atual.opcao4 = nova_opcao4.strip()

                                session.commit()
                                st.success("✅ Enquete atualizada com sucesso!")
                        except Exception as e:
                            session.rollback()
                            st.error(f"🚨 Erro ao salvar alterações: {e}")

                # Botão para excluir a enquete
                st.markdown("---")
                st.subheader("Excluir Enquete")
                st.warning("⚠️ A exclusão é permanente e não pode ser desfeita.")

                confirmar_exclusao = st.checkbox("Sim, desejo excluir esta enquete", key="confirmar_exclusao_checkbox")
                if confirmar_exclusao:
                    if st.button("🗑️ Confirmar Exclusão", key="confirmar_exclusao_button"):
                        try:
                            session.delete(enquete_atual)
                            session.commit()
                            st.success("✅ Enquete excluída com sucesso!")
                            st.experimental_rerun()  # Recarrega a página após exclusão
                        except Exception as e:
                            session.rollback()
                            st.error(f"🚨 Erro ao excluir a enquete: {e}")
            else:
                st.warning("⚠️ Enquete não encontrada.")

    # Aba de Estatísticas
    with tab4:
        st.header("📈 Estatísticas das Enquetes")

        with Session() as session:
            # Consulta para contar o total de enquetes
            total_enquetes = session.execute(text("SELECT COUNT(*) FROM enquete_enquete")).scalar()

            # Consulta para contar o total de enquetes ativas
            enquetes_ativas = session.execute(text("SELECT COUNT(*) FROM enquete_enquete WHERE ativo = TRUE")).scalar()

            # Enquetes finalizadas
            enquetes_finalizadas = total_enquetes - enquetes_ativas

            # Consulta para contar o total de votações em enquetes ativas
            total_votacoes_ativas = session.execute(text("""
                SELECT COUNT(*) 
                FROM oraculo_votacao
                WHERE enquete_id IN (SELECT id FROM enquete_enquete WHERE ativo = TRUE)
            """)).scalar()

            # Consulta para contar o total de cargos direcionados
            total_cargos_direcionados = session.execute(text("""
                SELECT COUNT(DISTINCT cargo_id) 
                FROM enquete_enquete_direcionado_a
            """)).scalar()

        # Exibir métricas em 4 colunas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total de Enquetes", total_enquetes)
        with col2:
            st.metric("✅ Enquetes Ativas", enquetes_ativas)
        with col3:
            st.metric("❌ Enquetes Finalizadas", enquetes_finalizadas)
        with col4:
            st.metric("🗳️ Total de Votações em Enquetes Ativas", total_votacoes_ativas)

        # Gráfico de distribuição de enquetes (ativas vs finalizadas)
        fig1 = px.bar(
            x=["Ativas", "Finalizadas"],
            y=[enquetes_ativas, enquetes_finalizadas],
            labels={'x': "Status", 'y': "Quantidade"},
            title="📊 Distribuição de Enquetes",
            color_discrete_sequence=["#008000", "#FF4500"],  # Verde para ativas, vermelho para finalizadas
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico de pizza: Distribuição de votos por opção (para uma enquete selecionada)
        st.subheader("🔍 Detalhamento de Votos por Enquete")
        with Session() as session:
            # Lista de enquetes ativas para seleção
            enquetes_ativas_lista = session.execute(text("""
                SELECT id, titulo 
                FROM enquete_enquete 
                WHERE ativo = TRUE
            """)).fetchall()

            if not enquetes_ativas_lista:
                st.info("ℹ️ Nenhuma enquete ativa disponível para análise.")
            else:
                # Criar um dicionário para facilitar a seleção
                enquetes_ativas_dict = {enquete[1]: enquete[0] for enquete in enquetes_ativas_lista}
                enquete_selecionada = st.selectbox(
                    "Selecione uma enquete para analisar os votos:",
                    list(enquetes_ativas_dict.keys())
                )

                # Buscar os votos da enquete selecionada
                enquete_id = enquetes_ativas_dict[enquete_selecionada]
                votos_por_opcao = session.execute(text("""
                    SELECT opcao_votada, COUNT(*) AS total_votos
                    FROM oraculo_votacao
                    WHERE enquete_id = :enquete_id
                    GROUP BY opcao_votada
                """), {"enquete_id": enquete_id}).fetchall()

                if votos_por_opcao:
                    # Preparar dados para o gráfico
                    opcoes = [voto[0] for voto in votos_por_opcao]
                    votos = [voto[1] for voto in votos_por_opcao]

                    # Criar gráfico de pizza
                    fig2 = px.pie(
                        names=opcoes,
                        values=votos,
                        title=f"📊 Distribuição de Votos para '{enquete_selecionada}'",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info(f"ℹ️ Nenhum voto registrado para a enquete '{enquete_selecionada}'.")

        # Aplicar estilo aos cards 📌
        style_metric_cards(
            background_color="#008000",  # verde
            border_left_color="#FFFFFF",
            border_color="#000000",
            box_shadow="#FFFFFF"
        )


def exibir_enquetes(usuario_cargo_id):
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT e.id, e.titulo, e.descricao, e.data_inicio, e.data_fim, e.opcao1, e.opcao2, e.opcao3, e.opcao4
                FROM enquete_enquete e
                JOIN enquete_enquete_direcionado_a ed ON e.id = ed.enquete_id
                WHERE ed.cargo_id = :cargo_id
                  AND e.ativo = 1
                  AND e.data_inicio <= :hoje
                  AND e.data_fim >= :hoje
                ORDER BY e.data_inicio DESC
            """)
            hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            enquetes = connection.execute(query, {"cargo_id": usuario_cargo_id, "hoje": hoje}).fetchall()

            if not enquetes:
                st.info("ℹ️ Nenhuma enquete disponível no momento.")
                return

            for enquete in enquetes:
                st.subheader(enquete.titulo)
                st.write(f"Descrição: {enquete.descricao}")
                st.write(f"Opções: {enquete.opcao1}, {enquete.opcao2}, {enquete.opcao3}, {enquete.opcao4}")
                st.write(f"Disponível até: {enquete.data_fim.strftime('%d/%m/%Y %H:%M:%S')}")
                # Adicionar botão de voto aqui
    except Exception as e:
        st.error(f"Erro ao buscar enquetes: {str(e)}")