from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from model_base import ModelBase


class GestaoIgrejas(ModelBase):
    __tablename__ = "gestao_igrejas"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_dt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_dt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active_dt = Column(Boolean, nullable=False)

    # Informações gerais da igreja
    nome_igreja = Column(String(150), nullable=False)
    menu1 = Column(String(10), nullable=False)
    menu2 = Column(String(10), nullable=False)
    menu3 = Column(String(10), nullable=False)
    menu4 = Column(String(10), nullable=False)
    menu5 = Column(String(10), nullable=False)
    menu6 = Column(String(10), nullable=False)
    titulo1 = Column(String(15), nullable=False)
    descricao1 = Column(Text, nullable=False)
    subtitulo1 = Column(String(10), nullable=False)
    subtitulo2 = Column(String(10), nullable=False)
    titulo_link = Column(String(200), nullable=False)

    # Imagens e arquivos
    img_fundo = Column(String(100), nullable=True)
    titulo2 = Column(String(15), nullable=False)
    descricao2 = Column(Text, nullable=False)
    qrcode = Column(String(100), nullable=True)
    link_cadastro = Column(String(200), nullable=False)

    # Contatos e redes sociais
    local = Column(String(100), nullable=False)
    site = Column(String(100), nullable=False)
    whats = Column(String(11), nullable=False)
    face = Column(String(100), nullable=False)
    insta = Column(String(100), nullable=False)
    linke = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    cnpj = Column(String(14), nullable=False)

    # Logo da igreja
    logo = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<GestaoIgrejas(id={self.id}, nome_igreja='{self.nome_igreja}', active_dt={self.active_dt})>"