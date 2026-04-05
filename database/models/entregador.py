import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Entregador(ModelBase):
    """
    Tabela de entregadores do Chef Delivery.

    Um entregador pode opcionalmente estar vinculado a um
    usuário do sistema (FK usuario_id).
    """

    __tablename__ = "entregadores"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    usuario_id = sa.Column(
        sa.Integer, sa.ForeignKey("usuarios.id"),
        unique=True, nullable=True,
    )
    nome = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable=False, unique=True)
    whatsapp = sa.Column(sa.String(20), nullable=False, unique=True)
    modelo_moto = sa.Column(sa.String(100), nullable=True)
    imagem_perfil = sa.Column(sa.String(500), nullable=True)
    status = sa.Column(sa.String(20), nullable=False, default="ativo")
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)

    # ── Relacionamentos ──
    entregas = relationship("Entrega", back_populates="entregador")

    def __repr__(self):
        return (
            f"<Entregador(id={self.id}, nome='{self.nome}', "
            f"status='{self.status}')>"
        )
