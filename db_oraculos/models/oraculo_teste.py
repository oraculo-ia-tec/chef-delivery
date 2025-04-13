from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoTeste(ModelBase):
    __tablename__ = "oraculo_teste"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)  # E-mail do usuário (único)
    usuario = Column(String(255), nullable=False)  # Nome de usuário
    whatsapp = Column(String(20), nullable=False)  # Número de WhatsApp
    password = Column(String(255), nullable=False)  # Senha do usuário
    cargo_id = Column(Integer, ForeignKey('oraculo_cargo.id'), nullable=True)  # Chave estrangeira para oraculo_cargo

    # Relacionamento
    cargo = relationship("OraculoCargo", back_populates="testes")  # Relação com oraculo_cargo

    def __repr__(self):
        return f"<OraculoTeste(id={self.id}, usuario='{self.usuario}', email='{self.email}')>"