import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class Produto(ModelBase):
    __tablename__ = 'produtos'

    id = sa.Column(sa.Integer, primary_key=True)
    nome = sa.Column(sa.String(100), nullable=False)  # Nome do produto com comprimento máximo de 100
    preco = sa.Column(sa.Float, nullable=False)  # Preço do produto
    descricao = sa.Column(sa.String(500))  # Descrição com comprimento máximo de 500
    imagem = sa.Column(sa.String(255))  # Caminho da imagem com comprimento máximo de 255
    link_pagamento = sa.Column(sa.String(255))  # Link de pagamento com comprimento máximo de 255
    categoria_id = sa.Column(sa.Integer, sa.ForeignKey('categorias.id'))  # Chave estrangeira para categorias

    # Relacionamentos
    categoria = orm.relationship('Categoria', back_populates='produtos')
    compras = orm.relationship('Compra', order_by='Compra.id', back_populates='produto')  # Ajustado para 'produto'

    def __repr__(self) -> str:
        return f'<Produto: {self.nome}>'