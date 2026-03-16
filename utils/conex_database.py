from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.authors import User, Admin, Parceiro, Cliente  # Certifique-se de importar seus modelos corretamente

# URL de conexão com o banco de dados MySQL
DATABASE_URL = "mysql://root:root@localhost/frigorifico"  # Atualize conforme necessário

# Criação do motor de conexão
engine = create_engine(DATABASE_URL)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Criar as tabelas no banco de dados com base nos modelos
    User.metadata.create_all(bind=engine)
    Admin.metadata.create_all(bind=engine)
    Parceiro.metadata.create_all(bind=engine)
    Cliente.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()  # Isso irá criar as tabelas no banco de dados "frigorifico"
