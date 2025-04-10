import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class Loja(ModelBase):
    __tablename__ = 'lojas'

    id = sa.Column(sa.Integer, primary_key=True)
    nome = sa.Column(sa.String(100), nullable=False)  # Nome da lojas com comprimento máximo de 100
    endereco = sa.Column(sa.String(255))  # Endereço com comprimento máximo de 255
    telefone = sa.Column(sa.String(15))  # Telefone com comprimento máximo de 15
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))  # Chave estrangeira para usuários

    # Relacionamentos
    usuario = orm.relationship('User', back_populates='lojas')
    categorias = orm.relationship('Categoria', order_by='Categoria.id', back_populates='lojas', cascade='all, delete-orphan')
    contas = orm.relationship('Conta', back_populates='lojas', cascade='all, delete-orphan')  # Adicionando o relacionamento com Conta

    def __repr__(self) -> str:
        return f'<Loja: {self.nome}>'