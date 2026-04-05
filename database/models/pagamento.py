import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Pagamento(ModelBase):
    """
    Tabela de pagamentos do Chef Delivery.

    Cada pagamento está vinculado 1:1 a um pedido e N:1 a um usuário.
    Armazena dados do gateway ASAAS (payment_id, PIX, invoice) e
    status que é atualizado via webhook.
    """

    __tablename__ = "pagamentos"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    pedido_id = sa.Column(
        sa.Integer, sa.ForeignKey("pedidos.id"),
        nullable=False, unique=True, index=True,
    )
    usuario_id = sa.Column(
        sa.Integer, sa.ForeignKey("usuarios.id"),
        nullable=False, index=True,
    )
    asaas_payment_id = sa.Column(sa.String(100), unique=True, nullable=True)
    valor = sa.Column(sa.Numeric(10, 2), nullable=False)
    metodo_pagamento = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(30), nullable=False, default="pendente")
    data_pagamento = sa.Column(sa.DateTime, nullable=True)
    data_confirmacao = sa.Column(sa.DateTime, nullable=True)

    # Dados PIX
    pix_payload = sa.Column(sa.Text, nullable=True)
    pix_qr_code_base64 = sa.Column(sa.Text, nullable=True)
    pix_expiration_date = sa.Column(sa.DateTime, nullable=True)

    # Dados gerais do gateway
    invoice_url = sa.Column(sa.String(500), nullable=True)
    webhook_event = sa.Column(sa.String(100), nullable=True)

    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=utcnow,
                           onupdate=utcnow)

    # ── Relacionamentos ──
    pedido = relationship("Pedido", back_populates="pagamento")
    usuario = relationship("Usuario", back_populates="pagamentos")

    def __repr__(self):
        return (
            f"<Pagamento(id={self.id}, pedido_id={self.pedido_id}, "
            f"status='{self.status}')>"
        )
