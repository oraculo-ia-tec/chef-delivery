from sqlalchemy.orm import Session
from models.authors import User


def create_author(db: Session, email: str, password: str, role: str, cpf: str):
    db_author = User(email=email, password=password, role=role, cpf=cpf)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_author_by_id(db: Session, author_id: int):
    return db.query(User).filter(User.id == author_id).first()


def get_author_by_cpf(db: Session, cpf: str):
    return db.query(User).filter(User.cpf == cpf).first()

