from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoEventoParticipantes(ModelBase):
    __tablename__ = "oraculo_evento_participantes"

    # Colunas principais
    evento_id = Column(Integer, ForeignKey('oraculo_evento.id'), primary_key=True)  # Chave estrangeira para oraculo_evento
    usuario_id = Column(Integer, ForeignKey('oraculo_user.id'), primary_key=True)  # Chave estrangeira para oraculo_user
    checkin = Column(Boolean, nullable=False, default=False)  # Check-in realizado (padrão False)
    data_inscricao = Column(DateTime, nullable=False, default="CURRENT_TIMESTAMP")  # Data e hora da inscrição

    # Relacionamentos
    evento = relationship("OraculoEvento", back_populates="participantes")  # Relação com oraculo_evento
    usuario = relationship("OraculoUser", back_populates="eventos_participados")  # Relação com oraculo_user

    def __repr__(self):
        return f"<OraculoEventoParticipantes(evento_id={self.evento_id}, usuario_id={self.usuario_id}, checkin={self.checkin})>"