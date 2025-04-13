from sqlalchemy import Column, Integer, Numeric, Enum, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class PagamentosAsaas(ModelBase):
    __tablename__ = "pagamentos_asaas"

    # Colunas principais
    id = Column(Integer, primary_key=True)  # Chave primária
    usuario_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=True)  # Chave estrangeira para oraculo_user
    valor = Column(Numeric(10, 2), nullable=True)  # Valor do pagamento
    status = Column(Enum('Pendente', 'Pago', 'Cancelado'), nullable=True)  # Status do pagamento
    metodo_pagamento = Column(Enum('Pix', 'Cartao', 'Boleto'), nullable=True)  # Método de pagamento
    referencia_id = Column(Integer, nullable=True)  # ID de referência
    data_criacao = Column(DateTime, nullable=True)  # Data e hora de criação
    data_vencimento = Column(DateTime, nullable=True)  # Data e hora de vencimento
    hora_pagamento = Column(Time, nullable=True)  # Hora do pagamento

    # Relacionamento
    usuario = relationship("OraculoUser", back_populates="pagamentos")  # Relação com oraculo_user

    def __repr__(self):
        return f"<PagamentosAsaas(id={self.id}, usuario_id={self.usuario_id}, valor={self.valor}, status='{self.status}')>"