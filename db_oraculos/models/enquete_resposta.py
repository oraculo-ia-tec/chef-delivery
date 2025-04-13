from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class EnqueteResposta(ModelBase):
    __tablename__ = "enquete_resposta"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    resposta = Column(String(255), nullable=False)  # Resposta fornecida pelo usuário
    explicacao = Column(Text, nullable=True)  # Explicação detalhada ou justificativa
    enquete_id = Column(Integer, ForeignKey('enquete_enquete.id'), nullable=False)  # Chave estrangeira para enquete_enquete
    usuario_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=False)  # Chave estrangeira para oraculo_user

    # Relacionamentos
    enquete = relationship("EnqueteEnquete", back_populates="respostas")  # Relação com enquete_enquete
    usuario = relationship("OraculoUser", back_populates="respostas")  # Relação com oraculo_user

    def __repr__(self):
        return f"<EnqueteResposta(id={self.id}, resposta='{self.resposta}', usuario_id={self.usuario_id})>"