import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.models.model_base import ModelBase, utcnow


class Usuario(ModelBase):
    """
    Tabela de usuários do sistema Chef Delivery.

    Armazena dados de autenticação, autorização, contato,
    endereço e referência da imagem de perfil.
    Roles: admin | parceiro | cliente | entregador
    """

    __tablename__ = "usuarios"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nome = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable=False, unique=True, index=True)
    whatsapp = sa.Column(sa.String(20), nullable=False, unique=True)
    cpf_cnpj = sa.Column(sa.String(18), unique=True, nullable=True)
    senha_hash = sa.Column(sa.String(255), nullable=False)
    role = sa.Column(sa.String(20), nullable=False, default="cliente")
    ativo = sa.Column(sa.Boolean, nullable=False, default=True)
    email_verificado = sa.Column(sa.Boolean, nullable=False, default=False)
    imagem_perfil = sa.Column(sa.String(500), nullable=True)

    # Endereço
    endereco = sa.Column(sa.String(500), nullable=True)
    numero = sa.Column(sa.String(20), nullable=True)
    complemento = sa.Column(sa.String(255), nullable=True)
    bairro = sa.Column(sa.String(255), nullable=True)
    cidade = sa.Column(sa.String(255), nullable=True)
    cep = sa.Column(sa.String(10), nullable=True)

    created_at = sa.Column(sa.DateTime, nullable=False, default=utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=utcnow,
                           onupdate=utcnow)

    # ── Relacionamentos ──
    pedidos = relationship(
        "Pedido", back_populates="usuario", cascade="all, delete-orphan"
    )
    pagamentos = relationship(
        "Pagamento", back_populates="usuario", cascade="all, delete-orphan"
    )
    parceiro = relationship(
        "Parceiro", back_populates="usuario", uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', role='{self.role}')>"
