from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoLoja(ModelBase):
    __tablename__ = "oraculo_loja"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=True)  # Nome da loja (opcional)
    descricao = Column(Text, nullable=True)  # Descrição detalhada da loja (opcional)
    cnpj = Column(String(20), nullable=True)  # CNPJ da loja (opcional)
    telefone = Column(String(20), nullable=True)  # Telefone de contato (opcional)
    email = Column(String(255), nullable=True)  # E-mail de contato (opcional)
    endereco = Column(String(255), nullable=True)  # Endereço da loja (opcional)
    cep = Column(String(10), nullable=True)  # CEP do endereço (opcional)
    bairro = Column(String(100), nullable=True)  # Bairro da loja (opcional)
    cidade = Column(String(100), nullable=True)  # Cidade da loja (opcional)
    estado = Column(String(50), nullable=True)  # Estado da loja (opcional)
    user_id = Column(Integer, ForeignKey('oraculo_user.id'), nullable=True)  # Chave estrangeira para oraculo_user
    created_at = Column(DateTime, nullable=True)  # Data e hora de criação
    updated_at = Column(DateTime, nullable=True)  # Data e hora da última atualização
    status = Column(Boolean, nullable=True)  # Status da loja (ativo/inativo)
    categoria_id = Column(Integer, ForeignKey('categoria_loja.id'), nullable=True)  # Chave estrangeira para categoria_loja

    # Relacionamentos
    usuario = relationship("OraculoUser", back_populates="lojas")  # Relação com oraculo_user
    categoria = relationship("CategoriaLoja", back_populates="lojas")  # Relação com categoria_loja

    def __repr__(self):
        return f"<OraculoLoja(id={self.id}, nome='{self.nome}', status={self.status})>"