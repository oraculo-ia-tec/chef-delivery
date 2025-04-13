from sqlalchemy import Column, Integer, String
from model_base import ModelBase


class OraculoCargo(ModelBase):
    __tablename__ = "oraculo_cargo"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)  # Garante unicidade no nome do cargo

    def __repr__(self):
        return f"<OraculoCargo(id={self.id}, name='{self.name}')>"