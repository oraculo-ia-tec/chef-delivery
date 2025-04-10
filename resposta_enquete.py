import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime
from key_config import DATABASE_URL
from pytz import timezone



# Configuração do banco de dados
engine = create_engine(DATABASE_URL)

# Definir fuso horário
hoje = datetime.now(timezone('America/Sao_Paulo'))

# Função para buscar enquetes direcionadas ao cargo do usuário
def buscar_enquetes_por_cargo(cargo_nome):
    """Busca enquetes direcionadas ao cargo especificado."""
    cargo_id = obter_id_cargo(cargo_nome)
    if not cargo_id:
        st.warning(f"⚠️ O cargo '{cargo_nome}' não está cadastrado.")
        return []

    st.write(f"Buscando enquetes para o cargo com ID: {cargo_id}")
    with engine.connect() as connection:
        query = text("""
            SELECT e.id, e.titulo, e.descricao, e.data_inicio, e.data_fim, e.ativo, e.opcao1, e.opcao2, e.opcao3, e.opcao4
            FROM enquete_enquete e
            JOIN enquete_enquete_direcionado_a eda ON e.id = eda.enquete_id
            WHERE eda.cargo_id = :cargo_id AND e.ativo = 1 AND e.data_fim >= :hoje
        """)
        result = connection.execute(query, {"cargo_id": cargo_id, "hoje": hoje}).fetchall()
        st.write(f"Resultados encontrados: {result}")
        return result


# Função para salvar a resposta na tabela oraculo_votacao
def salvar_resposta(enquete_id, usuario_id, opcao_votada):
    """
    Salva a resposta do usuário na tabela oraculo_votacao.
    """
    try:
        # Verifica se o usuário já votou nesta enquete
        if verificar_voto_existente(enquete_id, usuario_id):
            st.warning(f"⚠️ Você já respondeu à enquete com ID '{enquete_id}'.")
            return False

        with engine.connect() as connection:
            query = text("""
                INSERT INTO oraculo_votacao (enquete_id, usuario_id, opcao_votada, created_dt)
                VALUES (:enquete_id, :usuario_id, :opcao_votada, :created_dt)
            """)
            connection.execute(
                query,
                {
                    "enquete_id": enquete_id,
                    "usuario_id": usuario_id,
                    "opcao_votada": opcao_votada,
                    "created_dt": hoje
                }
            )
            connection.commit()
            return True  # Retorna True se a inserção for bem-sucedida
    except Exception as e:
        st.error(f"Erro ao salvar resposta para a enquete '{enquete_id}' e usuário '{usuario_id}': {str(e)}")
        return False  # Retorna False em caso de erro


# Função para obter o ID do cargo com base no nome
def obter_id_cargo(cargo_nome):
    """Busca o ID do cargo com base no nome."""
    with engine.connect() as connection:
        query = text("SELECT id FROM oraculo_cargo WHERE name = :nome_cargo")
        result = connection.execute(query, {"nome_cargo": cargo_nome}).fetchone()
        return result[0] if result and result[0] else None


# Função para verificar se o usuário já votou na enquete
def verificar_voto_existente(enquete_id, usuario_id):
    """Verifica se o usuário já votou na enquete."""
    with engine.connect() as connection:
        query = text("""
            SELECT COUNT(*) 
            FROM oraculo_votacao 
            WHERE enquete_id = :enquete_id AND usuario_id = :usuario_id
        """)
        result = connection.execute(query, {"enquete_id": enquete_id, "usuario_id": usuario_id}).scalar()
        return result > 0


# Função principal para exibir enquetes e registrar respostas
def resposta_enquete(usuario_id, cargo_nome):
    """Exibe enquetes direcionadas ao cargo do usuário logado."""
    st.title("🗳️ Responder Enquetes")

    # Verifica se o cargo existe
    cargo_id = obter_id_cargo(cargo_nome)
    if not cargo_id:
        st.warning(f"⚠️ O cargo '{cargo_nome}' não está cadastrado.")
        return

    # Busca as enquetes direcionadas ao cargo
    enquetes = buscar_enquetes_por_cargo(cargo_nome)
    if not enquetes:
        st.info("ℹ️ Nenhuma enquete disponível para o seu cargo no momento.")
        return

    # Exibe as enquetes encontradas
    for enquete in enquetes:
        (
            enquete_id,
            titulo,
            descricao,
            data_inicio,
            data_fim,
            ativo,
            opcao1,
            opcao2,
            opcao3,
            opcao4,
        ) = enquete

        with st.expander(f"📋 {titulo} (Encerra em {data_fim.strftime('%d/%m/%Y')})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Descrição:** {descricao}")
                st.write(f"**Período:** {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}")

            with col2:
                st.write("**Opções disponíveis:**")
                opcoes = [opcao for opcao in [opcao1, opcao2, opcao3, opcao4] if opcao]
                opcao_escolhida = st.radio(
                    "Selecione sua resposta:",
                    opcoes,
                    key=f"enquete_{enquete_id}",
                )

            # Formulário para enviar a resposta
            with st.form(key=f"form_{enquete_id}", clear_on_submit=True):
                submit_button = st.form_submit_button("Enviar Resposta")

                if submit_button:
                    sucesso = salvar_resposta(enquete_id, usuario_id, opcao_escolhida)
                    if sucesso:
                        st.success(f"🎉 Sua resposta para a enquete '{titulo}' foi registrada!")
                        st.session_state[f"form_{enquete_id}"] = {}  # Limpa o estado do formulário
                    else:
                        st.error(f"⚠️ Falha ao registrar a resposta para a enquete '{titulo}'. Tente novamente.")