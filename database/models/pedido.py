import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Pedido(ModelBase):
    """
    Tabela de pedidos do Chef Delivery.

    Ciclo de status:
        aguardando_pagamento → pago → preparando → pronto →
        em_entrega → entregue | cancelado

    O campo valor_total é desnormalizado (poderia ser calculado
    a partir de SUM(itens_pedido.subtotal)) para performance e
    registro histórico.
    """

    __tablename__ = "pedidos"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    codigo = sa.Column(sa.String(50), nullable=False, unique=True, index=True)
    usuario_id = sa.Column(
        sa.Integer, sa.ForeignKey("usuarios.id"),
        nullable=False, index=True,
    )
    endereco_entrega = sa.Column(sa.Text, nullable=False)
    observacao = sa.Column(sa.Text, nullable=True)
    valor_total = sa.Column(sa.Numeric(10, 2), nullable=False)
    status = sa.Column(
        sa.String(30), nullable=False, default="aguardando_pagamento"
    )
    horario_chegada = sa.Column(sa.DateTime, nullable=True)
    inicio_preparacao = sa.Column(sa.DateTime, nullable=True)
    fim_preparacao = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=utcnow,
                           onupdate=utcnow)

    # ── Relacionamentos ──
    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship(
        "ItemPedido", back_populates="pedido", cascade="all, delete-orphan"
    )
    pagamento = relationship(
        "Pagamento", back_populates="pedido", uselist=False,
        cascade="all, delete-orphan",
    )
    entrega = relationship(
        "Entrega", back_populates="pedido", uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Pedido(id={self.id}, codigo='{self.codigo}', "
            f"status='{self.status}')>"
        )
