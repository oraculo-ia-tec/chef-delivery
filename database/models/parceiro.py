import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Parceiro(ModelBase):
    """
    Tabela de parceiros comerciais.

    Cada parceiro está vinculado 1:1 a um usuário do sistema
    com role='parceiro'.
    """

    __tablename__ = "parceiros"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    usuario_id = sa.Column(
        sa.Integer, sa.ForeignKey("usuarios.id"),
        nullable=False, unique=True,
    )
    razao_social = sa.Column(sa.String(255), nullable=True)
    cnpj = sa.Column(sa.String(18), unique=True, nullable=True)
    tipo_negocio = sa.Column(sa.String(100), nullable=True)
    status = sa.Column(sa.String(20), nullable=False, default="ativo")
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)

    # ── Relacionamentos ──
    usuario = relationship("Usuario", back_populates="parceiro")

    def __repr__(self):
        return (
            f"<Parceiro(id={self.id}, "
            f"razao_social='{self.razao_social}')>"
        )
