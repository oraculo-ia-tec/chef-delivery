import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.future.engine import Engine
from oraculo.__models_oraculo.model_base import ModelBase
from decouple import config


class DBSessionManager:
    """
    Classe para gerenciar a conexão e sessões do banco de dados.
    """
    __engine: Optional[Engine] = None

    @staticmethod
    def create_engine() -> Engine:
        """
        Configura a conexão ao banco de dados.
        """
        if DBSessionManager.__engine:
            return DBSessionManager.__engine

        try:
            conn_str = config("DATABASE_URL")
            DBSessionManager.__engine = sa.create_engine(url=conn_str, echo=False)
            return DBSessionManager.__engine
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")

    @staticmethod
    def create_session() -> Session:
        """
        Cria uma sessão de conexão ao banco de dados.
        """
        if not DBSessionManager.__engine:
            DBSessionManager.create_engine()

        __session = sessionmaker(DBSessionManager.__engine, expire_on_commit=False, class_=Session)
        session: Session = __session()
        return session

    @staticmethod
    def create_tables(drop_existing: bool = False) -> None:
        """
        Cria as tabelas no banco de dados.
        :param drop_existing: Se True, exclui todas as tabelas existentes antes de criar novas.
        """
        if not DBSessionManager.__engine:
            DBSessionManager.create_engine()

        if drop_existing:
            print("⚠️ ATENÇÃO: Todas as tabelas existentes serão excluídas!")
            ModelBase.metadata.drop_all(DBSessionManager.__engine)

        ModelBase.metadata.create_all(DBSessionManager.__engine)
        print("✅ Tabelas criadas com sucesso!")


# Funções públicas para uso externo
def get_engine() -> Engine:
    return DBSessionManager.create_engine()


def get_session() -> Session:
    return DBSessionManager.create_session()

def setup_database(drop_existing: bool = False) -> None:
    DBSessionManager.create_tables(drop_existing)


def test_connection(engine: Engine):
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        print("✅ Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        raise ConnectionError(f"Erro ao testar a conexão com o banco de dados: {e}")