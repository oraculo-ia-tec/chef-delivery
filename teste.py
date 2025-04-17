import streamlit as st
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (create_engine, Column, BigInteger, String, Numeric, DateTime, ForeignKey, Enum,
                        Time, Boolean)
from datetime import datetime
from enum import Enum as PyEnum  # Renomeado para evitar conflito
from key_config import DATABASE_URL, ASAAS_API_KEY, BASE_URL_ASAAS
from httpx import AsyncClient
import asyncio

# Configuração do banco de dados
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Criar ou atualizar o esquema do banco de dados
Base.metadata.create_all(engine)

class DiaCulto(PyEnum):  # Enumeração Python
    segunda = 'Segunda'
    terca = 'Terça'
    quarta = 'Quarta'
    quinta = 'Quinta'
    sexta = 'Sexta'
    sabado = 'Sábado'
    domingo = 'Domingo'

class OraculoCulto(Base):
    __tablename__ = 'oraculo_culto'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome_culto = Column(String(255), nullable=False)
    nome_pregador = Column(String(255), nullable=False)
    titulo_pregacao = Column(String(255), nullable=False)
    diaconato = Column(String(255), nullable=True)
    grupo_louvor = Column(String(255), nullable=True)
    dia_culto = Column(Enum(DiaCulto, name="dia_culto_enum"), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    pastor_responsavel = Column(BigInteger, ForeignKey('oraculo_user.id'), nullable=True)
    departamento_infantil = Column(Boolean, default=False)
    link_dizimo = Column(String(500), nullable=True)
    link_oferta = Column(String(500), nullable=True)
    qrcode_dizimo = Column(String(500), nullable=True)
    qrcode_oferta = Column(String(500), nullable=True)

class Dizimo(Base):
    __tablename__ = 'dizimo'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2))
    oraculo_culto_id = Column(BigInteger, ForeignKey('oraculo_culto.id'))
    payment_id = Column(String(255), nullable=True)  # Nova coluna adicionada
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Oferta(Base):
    __tablename__ = 'oferta'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2))
    oraculo_culto_id = Column(BigInteger, ForeignKey('oraculo_culto.id'))
    payment_id = Column(String(255), nullable=True)  # Nova coluna adicionada
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

async def criar_cobranca(valor: float, descricao: str, customerId: str):
    async with AsyncClient() as client:
        response = await client.post(
            f'{BASE_URL_ASAAS}/payments',
            headers={'access_token': ASAAS_API_KEY},
            json={
                "value": valor,
                "description": descricao,
                "customerId": customerId,
                "paymentMethod": "CREDIT_CARD",
                "dueDate": datetime.now().strftime("%Y-%m-%d")
            }
        )
        response.raise_for_status()
        return response.json()

async def show_dizimo_oferta():
    with Session() as session:
        cultos = session.query(OraculoCulto).all()
        if not cultos:
            st.warning("⚠️ Nenhum culto registrado no sistema.")
            return

        culto_options = {culto.nome_culto: culto for culto in cultos}

        st.header("📅 Selecione o Culto")
        culto_selecionado_nome = st.selectbox(
            "Escolha o culto:",
            options=list(culto_options.keys())
        )
        culto_selecionado = culto_options[culto_selecionado_nome]

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
                payment_response_dizimo = await criar_cobranca(valor_dizimo, "Dízimo referente ao culto", culto_selecionado.id)
                payment_response_oferta = await criar_cobranca(valor_oferta, "Oferta referente ao culto", culto_selecionado.id)

                novo_dizimo = Dizimo(
                    valor_total=valor_dizimo,
                    oraculo_culto_id=culto_selecionado.id,
                    payment_id=payment_response_dizimo['id'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                nova_oferta = Oferta(
                    valor_total=valor_oferta,
                    oraculo_culto_id=culto_selecionado.id,
                    payment_id=payment_response_oferta['id'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                session.add(novo_dizimo)
                session.add(nova_oferta)
                session.commit()

                st.success("Dízimos e ofertas registrados com sucesso!")

        st.header("📊 Registros Salvos")
        dizimos = session.query(Dizimo).join(OraculoCulto).all()
        if dizimos:
            st.subheader("📋 Dízimos Registrados")
            for dizimo in dizimos:
                st.write(f"**Culto:** {dizimo.oraculo_culto.nome_culto}")
                st.write(f"Valor Total: R$ {dizimo.valor_total:.2f}")
                st.write(f"Payment ID: {dizimo.payment_id}")
                if dizimo.oraculo_culto.qrcode_dizimo:
                    st.image(dizimo.oraculo_culto.qrcode_dizimo, caption="QR Code do Dízimo", use_column_width=True)
                st.write(f"Data e Hora: {dizimo.created_at.strftime('%d/%m/%Y %H:%M')}")
                st.markdown("---")

        ofertas = session.query(Oferta).join(OraculoCulto).all()
        if ofertas:
            st.subheader("📋 Ofertas Registradas")
            for oferta in ofertas:
                st.write(f"**Culto:** {oferta.oraculo_culto.nome_culto}")
                st.write(f"Valor Total: R$ {oferta.valor_total:.2f}")
                st.write(f"Payment ID: {oferta.payment_id}")
                if oferta.oraculo_culto.qrcode_oferta:
                    st.image(oferta.oraculo_culto.qrcode_oferta, caption="QR Code da Oferta", use_column_width=True)
                st.write(f"Data e Hora: {oferta.created_at.strftime('%d/%m/%Y %H:%M')}")
                st.markdown("---")

if __name__ == "__main__":
    st.set_page_config(page_title="Dízimos e Ofertas", page_icon="🙏", layout="wide")
    asyncio.run(show_dizimo_oferta())