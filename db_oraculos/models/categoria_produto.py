from sqlalchemy import Column, Integer, String
from model_base import ModelBase  # Importando ModelBase

class CategoriaProduto(ModelBase):
    __tablename__ = "categoria_produto"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)  # Nome da categoria (obrigatório)
    descricao = Column(String(255), nullable=True)  # Descrição opcional

    def __repr__(self):
        return f"<CategoriaProduto(id={self.id}, nome='{self.nome}')>"