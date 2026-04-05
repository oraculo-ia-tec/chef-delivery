import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Categoria(ModelBase):
    """
    Tabela de categorias de produtos.

    Cada categoria agrupa produtos do mesmo tipo
    (ex.: Boi, Porco, Frango) com unidade padrão (kg ou un).
    """

    __tablename__ = "categorias"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nome = sa.Column(sa.String(100), nullable=False, unique=True)
    icone = sa.Column(sa.String(10), nullable=True)
    unidade_padrao = sa.Column(sa.String(10), nullable=False, default="kg")
    ativo = sa.Column(sa.Boolean, nullable=False, default=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)

    # ── Relacionamentos ──
    produtos = relationship(
        "Produto", back_populates="categoria", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"
