from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoVotacao(ModelBase):
    __tablename__ = "oraculo_votacao"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    enquete_id = Column(Integer, ForeignKey('enquete_enquete.id'), nullable=False)  # Chave estrangeira para enquete_enquete
    usuario_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=False)  # Chave estrangeira para oraculo_user
    opcao_votada = Column(String(200), nullable=False)  # Opção escolhida pelo usuário
    created_dt = Column(TIMESTAMP, nullable=True, default="CURRENT_TIMESTAMP")  # Data e hora de criação

    # Relacionamentos
    enquete = relationship("EnqueteEnquete", back_populates="votos")  # Relação com enquete_enquete
    usuario = relationship("OraculoUser", back_populates="votos")  # Relação com oraculo_user

    def __repr__(self):
        return f"<OraculoVotacao(id={self.id}, enquete_id={self.enquete_id}, usuario_id={self.usuario_id}, opcao_votada='{self.opcao_votada}')>"