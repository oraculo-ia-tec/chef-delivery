from sqlalchemy import Column, Integer, String, Enum, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoCulto(ModelBase):
    __tablename__ = "oraculo_culto"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_culto = Column(String(255), nullable=False)
    nome_pregador = Column(String(255), nullable=False)
    titulo_pregacao = Column(String(255), nullable=False)
    diaconato = Column(String(255), nullable=True)
    grupo_louvor = Column(String(255), nullable=True)
    dia_culto = Column(Enum('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    pastor_responsavel = Column(Integer, ForeignKey('oraculo_user.id'), nullable=True)
    departamento_infantil = Column(Boolean, nullable=True)
    link_dizimo = Column(String(500), nullable=True)
    link_oferta = Column(String(500), nullable=True)
    qrcode_dizimo = Column(String(500), nullable=True)
    qrcode_oferta = Column(String(500), nullable=True)

    # Relacionamento com a tabela oraculo_user
    pastor = relationship("OraculoUser", back_populates="cultos")

    def __repr__(self):
        return f"<OraculoCulto(id={self.id}, nome_culto='{self.nome_culto}', nome_pregador='{self.nome_pregador}')>"