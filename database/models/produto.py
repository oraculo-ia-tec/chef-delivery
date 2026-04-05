import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Produto(ModelBase):
    """
    Tabela de produtos do catálogo Chef Delivery.

    Cada produto pertence a uma única categoria.
    Constraint UNIQUE(categoria_id, nome) garante que não haja
    duplicação de nome dentro da mesma categoria.
    """

    __tablename__ = "produtos"
    __table_args__ = (
        sa.UniqueConstraint(
            "categoria_id", "nome", name="uq_produto_categoria_nome"
        ),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    categoria_id = sa.Column(
        sa.Integer, sa.ForeignKey("categorias.id"),
        nullable=False, index=True,
    )
    nome = sa.Column(sa.String(255), nullable=False)
    preco = sa.Column(sa.Numeric(10, 2), nullable=False)
    unidade = sa.Column(sa.String(10), nullable=False, default="kg")
    ativo = sa.Column(sa.Boolean, nullable=False, default=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=utcnow,
                           onupdate=utcnow)

    # ── Relacionamentos ──
    categoria = relationship("Categoria", back_populates="produtos")
    itens_pedido = relationship("ItemPedido", back_populates="produto")

    def __repr__(self):
        return (
            f"<Produto(id={self.id}, nome='{self.nome}', "
            f"preco={self.preco})>"
        )
