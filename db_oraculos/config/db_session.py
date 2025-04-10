import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.future.engine import Engine
from oraculo.__models_oraculo.model_base import ModelBase
from decouple import config


__engine: Optional[Engine] = None



def create_engine(sqlite: bool = False) -> Engine:
    """
    Função para configurar a conexão ao banco de dados.
    """
    global __engine

    if __engine:
        return

    conn_str = config("DATABASE_URL")  # Adicione a URL do seu banco de dados aqui
    __engine = sa.create_engine(url=conn_str, echo=False)

    return __engine


def create_session() -> Session:
    """
    Função para criar sessão de conexao ao banco de dados.
    """
    global __engine

    if not __engine:
        create_engine()  # create_engine(sqlite=True)

    __session = sessionmaker(__engine, expire_on_commit=False, class_=Session)

    session: Session = __session()

    return session


def create_tables() -> None:
    global __engine

    if not __engine:
        create_engine()

    # Criando as tabelas no banco de dados
    ModelBase.metadata.drop_all(__engine)  # Isso exclui todas as tabelas existentes
    ModelBase.metadata.create_all(__engine)  # Isso cria as novas tabelas
