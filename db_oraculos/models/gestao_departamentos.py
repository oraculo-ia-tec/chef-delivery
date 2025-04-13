from sqlalchemy import Column, Integer, String, Text, DateTime, TIMESTAMP
from model_base import ModelBase  # Importando ModelBase

class GestaoDepartamentos(ModelBase):
    __tablename__ = "gestao_departamentos"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_dt = Column(DateTime, nullable=False)
    updated_dt = Column(DateTime, nullable=False)
    active_dt = Column(TIMESTAMP, nullable=True, server_default="CURRENT_TIMESTAMP")
    departamento = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    img = Column(String(100), nullable=True)
    name_lider = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<GestaoDepartamentos(id={self.id}, departamento='{self.departamento}', lider='{self.name_lider}')>"