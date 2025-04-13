from sqlalchemy import Column, Integer, String, Text, Date, Time, Enum, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoEvento(ModelBase):
    __tablename__ = "oraculo_evento"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_evento = Column(String(100), nullable=False)  # Nome do evento
    tema_evento = Column(String(100), nullable=False)  # Tema do evento
    descricao = Column(Text, nullable=True)  # Descrição detalhada do evento
    data_evento = Column(Date, nullable=False)  # Data do evento
    hora_evento = Column(Time, nullable=False)  # Hora de início do evento
    hora_termino = Column(Time, nullable=False)  # Hora de término do evento
    local = Column(String(255), nullable=False)  # Local do evento
    tipo_evento = Column(Enum('gratuito', 'pago'), nullable=False)  # Tipo do evento
    preco = Column(Numeric(10, 2), nullable=False, default=0.00)  # Preço do evento
    max_participantes = Column(Integer, nullable=True)  # Número máximo de participantes
    palestrante = Column(String(100), nullable=True)  # Nome do palestrante
    biografia_palestrante = Column(Text, nullable=True)  # Biografia do palestrante
    foto_palestrante = Column(String(255), nullable=True)  # Foto do palestrante
    contato_email = Column(String(254), nullable=True)  # E-mail de contato
    contato_whatsapp = Column(String(20), nullable=True)  # WhatsApp de contato
    facebook_url = Column(String(255), nullable=True)  # URL do Facebook
    instagram_url = Column(String(255), nullable=True)  # URL do Instagram
    linkedin_url = Column(String(255), nullable=True)  # URL do LinkedIn
    banner = Column(String(255), nullable=True)  # Banner do evento
    responsavel_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=False)  # Chave estrangeira para oraculo_user
    status = Column(Enum('agendado', 'cancelado', 'realizado'), nullable=False, default='agendado')  # Status do evento
    created_at = Column(DateTime, nullable=False, default="CURRENT_TIMESTAMP")  # Data e hora de criação
    updated_at = Column(DateTime, nullable=True, onupdate="CURRENT_TIMESTAMP")  # Data e hora da última atualização
    cargo_permitido = Column(Integer, ForeignKey('oraculo_cargo.id'), nullable=True)  # Chave estrangeira para oraculo_cargo
    link_pagamento_id = Column(Integer, ForeignKey('financeiro.id'), nullable=True)  # Chave estrangeira para financeiro

    # Relacionamentos
    responsavel = relationship("OraculoUser", back_populates="eventos")  # Relação com oraculo_user
    cargo = relationship("OraculoCargo", back_populates="eventos")  # Relação com oraculo_cargo
    link_pagamento = relationship("Financeiro", back_populates="eventos")  # Relação com financeiro

    def __repr__(self):
        return f"<OraculoEvento(id={self.id}, nome_evento='{self.nome_evento}', status='{self.status}')>"