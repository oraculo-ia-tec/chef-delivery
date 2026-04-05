import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Entrega(ModelBase):
    """
    Tabela de entregas (víncula pedido ↔ entregador).

    Ciclo de status: atribuido → em_rota → entregue | devolvido
    Timestamps de saída e entrega são registrados automaticamente
    ao mudar o status.
    """

    __tablename__ = "entregas"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    pedido_id = sa.Column(
        sa.Integer, sa.ForeignKey("pedidos.id"),
        nullable=False, index=True,
    )
    entregador_id = sa.Column(
        sa.Integer, sa.ForeignKey("entregadores.id"),
        nullable=False, index=True,
    )
    status = sa.Column(sa.String(30), nullable=False, default="atribuido")
    horario_saida = sa.Column(sa.DateTime, nullable=True)
    horario_entrega = sa.Column(sa.DateTime, nullable=True)
    observacao = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=utcnow,
                           onupdate=utcnow)

    # ── Relacionamentos ──
    pedido = relationship("Pedido", back_populates="entrega")
    entregador = relationship("Entregador", back_populates="entregas")

    def __repr__(self):
        return (
            f"<Entrega(id={self.id}, pedido_id={self.pedido_id}, "
            f"status='{self.status}')>"
        )
