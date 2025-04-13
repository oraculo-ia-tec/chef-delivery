from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class GestaoCursos(ModelBase):
    __tablename__ = "gestao_cursos"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_dt = Column(DateTime, nullable=False)  # Data e hora de criação
    updated_dt = Column(DateTime, nullable=False)  # Data e hora da última atualização
    active_dt = Column(Boolean, nullable=False)  # Indica se o curso está ativo
    curso = Column(String(100), nullable=False)  # Nome do curso
    biografia = Column(Text, nullable=False)  # Descrição detalhada do curso
    valor = Column(Numeric(8, 2), nullable=False)  # Valor do curso
    inicio_curso = Column(DateTime, nullable=False)  # Data e hora de início do curso
    final_curso = Column(DateTime, nullable=False)  # Data e hora de término do curso
    professor_id = Column(Integer, ForeignKey('gestao_professores.id'), nullable=False)  # Chave estrangeira para gestao_professores

    # Relacionamento
    professor = relationship("GestaoProfessores", back_populates="cursos")  # Relação com gestao_professores

    def __repr__(self):
        return f"<GestaoCursos(id={self.id}, curso='{self.curso}', valor={self.valor})>"