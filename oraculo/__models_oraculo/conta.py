import sqlalchemy as sa
import sqlalchemy.orm as orm
from oraculo.__models_oraculo.model_base import ModelBase

class Conta(ModelBase):
    __tablename__ = 'contas'

    id = sa.Column(sa.Integer, primary_key=True)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)  # Chave estrangeira para o usuário
    saldo = sa.Column(sa.Float, default=0.0)  # Saldo inicial da conta
    loja_id = sa.Column(sa.Integer, sa.ForeignKey('lojas.id'), nullable=False)  # Chave estrangeira para a lojas

    # Relacionamentos
    usuario = orm.relationship('User', back_populates='contas')  # Relacionamento com o usuário
    loja = orm.relationship('Loja', back_populates='contas')  # Relacionamento com a lojas

    def __repr__(self) -> str:
        return f'<Conta: {self.id}, Saldo: {self.saldo}>'