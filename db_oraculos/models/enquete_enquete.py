from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class EnqueteEnquete(ModelBase):
    __tablename__ = "enquete_enquete"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)  # Título da enquete
    descricao = Column(Text, nullable=False)  # Descrição detalhada da enquete
    data_inicio = Column(DateTime, nullable=False)  # Data e hora de início
    data_fim = Column(DateTime, nullable=False)  # Data e hora de término
    ativo = Column(Boolean, nullable=False)  # Indica se a enquete está ativa
    opcao1 = Column(String(200), nullable=False)  # Primeira opção de resposta
    opcao2 = Column(String(200), nullable=False)  # Segunda opção de resposta
    opcao3 = Column(String(200), nullable=False)  # Terceira opção de resposta
    opcao4 = Column(String(200), nullable=False)  # Quarta opção de resposta
    created_dt = Column(DateTime, nullable=False)  # Data e hora de criação
    updated_dt = Column(DateTime, nullable=False)  # Data e hora da última atualização
    cargo_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=True)  # Chave estrangeira para oraculo_user

    # Relacionamento
    cargo = relationship("OraculoUser", back_populates="enquetes")  # Relação com oraculo_user

    def __repr__(self):
        return f"<EnqueteEnquete(id={self.id}, titulo='{self.titulo}', ativo={self.ativo})>"