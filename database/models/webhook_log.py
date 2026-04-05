import sqlalchemy as sa

from database.models.model_base import ModelBase, utcnow


class WebhookLog(ModelBase):
    """
    Tabela de auditoria de webhooks recebidos do ASAAS.

    Registra cada evento recebido, se foi processado com sucesso
    e o resultado da ação (confirmação, recusa, etc.).
    """

    __tablename__ = "webhook_logs"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    event_id = sa.Column(sa.String(100), nullable=True)
    event_type = sa.Column(sa.String(100), nullable=False)
    asaas_payment_id = sa.Column(sa.String(100), nullable=True, index=True)
    payload = sa.Column(sa.Text, nullable=False)
    processado = sa.Column(sa.Boolean, nullable=False, default=False)
    resultado = sa.Column(sa.String(255), nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)

    def __repr__(self):
        return (
            f"<WebhookLog(id={self.id}, event='{self.event_type}', "
            f"processado={self.processado})>"
        )
