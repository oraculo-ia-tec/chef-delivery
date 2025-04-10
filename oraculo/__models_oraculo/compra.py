import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class Compra(ModelBase):
    __tablename__ = 'compras'

    id = sa.Column(sa.Integer, primary_key=True)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    produto_id = sa.Column(sa.Integer, sa.ForeignKey('produtos.id'), nullable=False)
    quantidade = sa.Column(sa.Integer, nullable=False)
    valor_total = sa.Column(sa.Float, nullable=False)
    data_compra = sa.Column(sa.DateTime, default=sa.func.now())  # Ajustado para DateTime
    status = sa.Column(sa.String(50), default='pendente')  # Status da compra
    link_pagamento = sa.Column(sa.String(255))  # Link de pagamento associado à compra

    # Relacionamentos
    usuario = orm.relationship('User', back_populates='compras')
    produto = orm.relationship('Produto', back_populates='compras')  # Certifique-se de que a classe Produto tenha esse back_populates

    def __repr__(self) -> str:
        return f'<Compra: {self.id}, Usuário: {self.usuario_id}, Produto: {self.produto_id}>'