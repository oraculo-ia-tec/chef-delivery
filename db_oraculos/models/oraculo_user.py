from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoUser(ModelBase):
    __tablename__ = "oraculo_user"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cpf_cnpj = Column(String(20), nullable=False)
    email = Column(String(254), nullable=False)
    whatsapp = Column(String(15), nullable=False)
    endereco = Column(String(255), nullable=False)
    cep = Column(String(10), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    image = Column(String(100), nullable=True)
    created_at = Column(Date, nullable=False, server_default="CURRENT_DATE")
    created_time = Column(Time, nullable=False, server_default="CURRENT_TIME")
    deleted_at = Column(Date, nullable=True)
    deleted_time = Column(Time, nullable=True)
    cargo_id = Column(Integer, ForeignKey('oraculo_cargo.id'), nullable=True)
    decisao = Column(String(50), nullable=True)
    culto_id = Column(Integer, ForeignKey('oraculo_culto.id'), nullable=True)
    estado_civil = Column(String(20), nullable=True)
    filhos = Column(Integer, nullable=False, default=0)

    # Relacionamentos
    cargo = relationship("OraculoCargo", back_populates="usuarios")
    culto = relationship("OraculoCulto", back_populates="usuarios")

    def __repr__(self):
        return f"<OraculoUser(id={self.id}, username='{self.username}', name='{self.name}')>"