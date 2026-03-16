from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    cpfCnpj = Column(String)
    mobilePhone = Column(String)
    incomeValue = Column(Float)
    fixedPhone = Column(String)
    birthDate = Column(String)
    companyType = Column(String)
    address = Column(String)
    number = Column(String)
    complement = Column(String)
    province = Column(String)
    city = Column(String)
    neighborhood = Column(String)
    postalCode = Column(String)


class Admin(User):
    __tablename__ = 'admin'


class Parceiro(User):
    __tablename__ = 'parceiros'


class Cliente(User):
    __tablename__ = 'clientes'
