from sqlalchemy import Column, Integer, Enum, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class Financeiro(ModelBase):
    __tablename__ = "financeiro"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum('dizimo', 'oferta', 'evento', 'produto'), nullable=False)  # Tipo de transação
    valor = Column(Numeric(10, 2), nullable=False)  # Valor da transação
    status = Column(Enum('pendente', 'pago', 'cancelado'), nullable=False)  # Status da transação
    metodo_pagamento = Column(Enum('pix', 'cartao', 'boleto'), nullable=False)  # Método de pagamento
    referencia_id = Column(Integer, nullable=True)  # ID da tabela relacionada
    referencia_tabela = Column(String(50), nullable=False)  # Nome da tabela relacionada
    usuario_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=False)  # Chave estrangeira para oraculo_user
    created_at = Column(DateTime, nullable=False, default="CURRENT_TIMESTAMP")  # Data e hora de criação
    updated_at = Column(DateTime, nullable=False, default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")  # Última atualização

    # Relacionamento
    usuario = relationship("OraculoUser", back_populates="transacoes_financeiras")  # Relação com oraculo_user

    def __repr__(self):
        return f"<Financeiro(id={self.id}, tipo='{self.tipo}', valor={self.valor}, status='{self.status}')>"