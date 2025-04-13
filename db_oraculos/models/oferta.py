from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class Oferta(ModelBase):
    __tablename__ = "oferta"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2), nullable=False)  # Decimal com precisão de 10 dígitos e 2 casas decimais
    oraculo_culto_id = Column(Integer, ForeignKey('oraculo_culto.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP", onupdate=True)

    # Relacionamento com a tabela oraculo_culto
    culto = relationship("OraculoCulto", back_populates="ofertas")

    def __repr__(self):
        return f"<Oferta(id={self.id}, valor_total={self.valor_total}, oraculo_culto_id={self.oraculo_culto_id})>"