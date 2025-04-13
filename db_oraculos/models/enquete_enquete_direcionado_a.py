from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class EnqueteEnqueteDirecionadoA(ModelBase):
    __tablename__ = "enquete_enquete_direcionado_a"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    enquete_id = Column(Integer, ForeignKey('enquete_enquete.id'), nullable=False)  # Chave estrangeira para enquete_enquete
    cargo_id = Column(Integer, ForeignKey('oraculo_cargo.id'), nullable=False)  # Chave estrangeira para oraculo_cargo

    # Relacionamentos
    enquete = relationship("EnqueteEnquete", back_populates="direcionado_a")  # Relação com enquete_enquete
    cargo = relationship("OraculoCargo", back_populates="enquetes_direcionadas")  # Relação com oraculo_cargo

    def __repr__(self):
        return f"<EnqueteEnqueteDirecionadoA(id={self.id}, enquete_id={self.enquete_id}, cargo_id={self.cargo_id})>"