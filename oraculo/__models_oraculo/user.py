import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class User(ModelBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    cpf_cnpj = sa.Column(sa.String(14), nullable=False, unique=True)
    email = sa.Column(sa.String(255), nullable=False, unique=True)
    whatsapp = sa.Column(sa.String(15))
    endereco = sa.Column(sa.String(255))
    cep = sa.Column(sa.String(10))
    bairro = sa.Column(sa.String(100))
    cidade = sa.Column(sa.String(100))
    role = sa.Column(sa.String(50))
    username = sa.Column(sa.String(50), unique=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    image = sa.Column(sa.String(255))

    # Relacionamentos
    lojas = orm.relationship('Loja', back_populates='usuario', cascade='all, delete-orphan')
    contas = orm.relationship('Conta', back_populates='usuario', cascade='all, delete-orphan')
    compras = orm.relationship('Compra', order_by='Compra.id', back_populates='usuario', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Usuario: {self.username}>'

