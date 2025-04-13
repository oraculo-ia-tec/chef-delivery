from sqlalchemy import Column, Integer, String
from model_base import ModelBase  # Importando ModelBase

class CategoriaLoja(ModelBase):
    __tablename__ = "categoria_loja"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)  # Nome da categoria (único)
    descricao = Column(String(255), nullable=True)  # Descrição opcional

    def __repr__(self):
        return f"<CategoriaLoja(id={self.id}, nome='{self.nome}')>"