import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class Categoria(ModelBase):
    __tablename__ = 'categorias'

    id: int = sa.Column(sa.Integer, primary_key=True)
    nome: str = sa.Column(sa.String(100), nullable=False)  # Nome da categoria com comprimento máximo de 100
    loja_id: int = sa.Column(sa.Integer, sa.ForeignKey('lojas.id'))

    # Relacionamentos
    loja = orm.relationship('Loja', back_populates='categorias')
    produtos = orm.relationship('Produto', order_by='Produto.id', back_populates='categoria')

    def __repr__(self) -> str:
        return f'<Categoria: {self.nome}>'