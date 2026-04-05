import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase


class ItemPedido(ModelBase):
    """
    Tabela de itens de um pedido (junction pedidos ↔ produtos).

    O campo subtotal é desnormalizado (quantidade × preco_unitario)
    para preservar o valor exato no momento da compra.
    """

    __tablename__ = "itens_pedido"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    pedido_id = sa.Column(
        sa.Integer, sa.ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    produto_id = sa.Column(
        sa.Integer, sa.ForeignKey("produtos.id"),
        nullable=False, index=True,
    )
    quantidade = sa.Column(sa.Numeric(10, 3), nullable=False)
    preco_unitario = sa.Column(sa.Numeric(10, 2), nullable=False)
    subtotal = sa.Column(sa.Numeric(10, 2), nullable=False)

    # ── Relacionamentos ──
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")

    def __repr__(self):
        return (
            f"<ItemPedido(id={self.id}, produto_id={self.produto_id}, "
            f"qtd={self.quantidade})>"
        )
