from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from model_base import ModelBase  # Importando ModelBase

class OraculoProduto(ModelBase):
    __tablename__ = "oraculo_produto"

    # Colunas principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=True)  # Nome do produto
    descricao = Column(Text, nullable=True)  # Descrição detalhada
    preco = Column(Numeric(10, 2), nullable=True)  # Preço do produto
    estoque = Column(Integer, nullable=True)  # Quantidade em estoque
    imagem = Column(String(255), nullable=True)  # Caminho da imagem
    status = Column(Boolean, nullable=True)  # Status do produto (ativo/inativo)
    link = Column(String(500), nullable=True)  # Link para compra
    loja_id = Column(Integer, ForeignKey('oraculo_loja.id'), nullable=True)  # Chave estrangeira para oraculo_loja
    created_at = Column(DateTime, nullable=True)  # Data e hora de criação
    updated_at = Column(DateTime, nullable=True)  # Data e hora da última atualização
    categoria_id = Column(Integer, ForeignKey('categoria_produto.id'), nullable=True)  # Chave estrangeira para categoria_produto

    # Relacionamentos
    loja = relationship("OraculoLoja", back_populates="produtos")  # Relação com oraculo_loja
    categoria = relationship("CategoriaProduto", back_populates="produtos")  # Relação com categoria_produto

    def __repr__(self):
        return f"<OraculoProduto(id={self.id}, nome='{self.nome}', preco={self.preco}, estoque={self.estoque})>"