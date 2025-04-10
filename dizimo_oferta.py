import streamlit as st
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (create_engine, Column, BigInteger, String, Numeric, DateTime, ForeignKey, Enum,
                        Text, Time, Boolean,)
from datetime import datetime
from key_config import DATABASE_URL  # Certifique-se de que este arquivo contém a URL do banco de dados

# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class DiaCulto(Enum):
    segunda = 'Segunda'
    terca = 'Terca'
    quarta = 'Quarta'
    quinta = 'Quinta'
    sexta = 'Sexta'
    sabado = 'Sabado'
    domingo = 'Domingo'

# Definição das tabelas
class OraculoCulto(Base):
    __tablename__ = 'oraculo_culto'  # Nome da tabela no banco de dados

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # ID do culto
    nome_culto = Column(String(255), nullable=False)  # Nome do culto
    nome_pregador = Column(String(255), nullable=False)  # Nome do pregador
    titulo_pregacao = Column(String(255), nullable=False)  # Título da pregação
    diaconato = Column(String(255), nullable=True)  # Diaconato
    grupo_louvor = Column(String(255), nullable=True)  # Grupo de louvor
    dia_culto = DiaCulto
    hora_inicio = Column(Time, nullable=False)  # Hora de início
    hora_fim = Column(Time, nullable=False)  # Hora de fim
    pastor_responsavel = Column(BigInteger, ForeignKey('oraculo_user.id'), nullable=True)  # ID do pastor responsável
    departamento_infantil = Column(Boolean, default=False)  # Booleano para indicar se haverá departamento infantil
    link_dizimo = Column(String(500), nullable=True)  # Link para pagamento de dízimo
    link_oferta = Column(String(500), nullable=True)  # Link para pagamento de oferta
    qrcode_dizimo = Column(String(500), nullable=True)  # QR Code para pagamento de dízimo
    qrcode_oferta = Column(String(500), nullable=True)  # QR Code para pagamento de oferta

class Dizimo(Base):
    __tablename__ = 'dizimo'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2))
    oraculo_culto_id = Column(BigInteger, ForeignKey('oraculo_culto.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Oferta(Base):
    __tablename__ = 'oferta'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2))
    oraculo_culto_id = Column(BigInteger, ForeignKey('oraculo_culto.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


st.title("🙏 Registro de Dízimos e Ofertas 🙏")

# Conexão com o banco de dados
session = Session()

# Carregar cultos disponíveis
cultos = session.query(OraculoCulto).all()
culto_options = {culto.nome_culto: culto for culto in cultos}

# Seção para selecionar o culto
st.header("📅 Selecione o Culto")
culto_selecionado_nome = st.selectbox(
    "Escolha o culto:",
    options=list(culto_options.keys())
)
culto_selecionado = culto_options[culto_selecionado_nome]

def show_dizimo_oferta():
    # Carregar cultos disponíveis
    cultos = session.query(OraculoCulto).all()
    culto_options = {culto.nome_culto: culto for culto in cultos}

    # Seção para selecionar o culto
    st.header("📅 Selecione o Culto")
    culto_selecionado_nome = st.selectbox(
        "Escolha o culto:",
        options=list(culto_options.keys())
    )
    culto_selecionado = culto_options[culto_selecionado_nome]

    # Formulário para registrar dízimos e ofertas
    st.header("💰 Registrar Dízimos e Ofertas")
    with st.form(key="registro_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dízimos")
            valor_dizimo = st.number_input("Valor Total de Dízimos (R$)", min_value=0.0, step=0.01, format="%.2f")

        with col2:
            st.subheader("Ofertas")
            valor_oferta = st.number_input("Valor Total de Ofertas (R$)", min_value=0.0, step=0.01, format="%.2f")

        submit_button = st.form_submit_button("Registrar")

        if submit_button:
            # Salvar registros no banco de dados
            novo_dizimo = Dizimo(
                valor_total=valor_dizimo,
                oraculo_culto_id=culto_selecionado.id,
                created_at=datetime.now(),  # Data e hora atual
                updated_at=datetime.now()  # Data e hora atual
            )
            nova_oferta = Oferta(
                valor_total=valor_oferta,
                oraculo_culto_id=culto_selecionado.id,
                created_at=datetime.now(),  # Data e hora atual
                updated_at=datetime.now()  # Data e hora atual
            )

            session.add(novo_dizimo)
            session.add(nova_oferta)
            session.commit()

            st.success("Dízimos e ofertas registrados com sucesso!")

    # Exibir registros salvos
    st.header("📊 Registros Salvos")

    # Consultar registros de dízimos
    dizimos = session.query(Dizimo).join(OraculoCulto).all()
    if dizimos:
        st.subheader("📋 Dízimos Registrados")
        for dizimo in dizimos:
            st.write(f"**Culto:** {dizimo.oraculo_culto.nome_culto}")
            st.write(f"Valor Total: R$ {dizimo.valor_total:.2f}")
            st.image(dizimo.oraculo_culto.qrcode, caption="QR Code do Culto", use_column_width=True)
            st.write(f"Data e Hora: {dizimo.created_at.strftime('%d/%m/%Y %H:%M')}")
            st.markdown("---")

    # Consultar registros de ofertas
    ofertas = session.query(Oferta).join(OraculoCulto).all()
    if ofertas:
        st.subheader("📋 Ofertas Registradas")
        for oferta in ofertas:
            st.write(f"**Culto:** {oferta.oraculo_culto.nome_culto}")
            st.write(f"Valor Total: R$ {oferta.valor_total:.2f}")
            st.image(oferta.oraculo_culto.qrcode, caption="QR Code do Culto", use_column_width=True)
            st.write(f"Data e Hora: {oferta.created_at.strftime('%d/%m/%Y %H:%M')}")
            st.markdown("---")

    # Fechar sessão
    session.close()


if __name__ == "__main__":
    st.set_page_config(page_title="Dízimos e Ofertas", page_icon="🙏", layout="wide")
    show_dizimo_oferta()