from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.conex_database import SessionLocal
from sessoes.sessoes import create_author, get_author_by_id, get_author_by_cpf
from models.authors import User
from pydantic import BaseModel
import bcrypt

router = APIRouter()


class RegisterRequest(User):
    email: str
    password: str
    role: str
    cpf: str


@router.post("/register")
async def register(request: RegisterRequest):
    db: Session = SessionLocal()
    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
    try:
        author = create_author(db, request.email, hashed_password.decode('utf-8'), request.role, request.cpf)
        return {"message": "Cadastrado com sucesso!", "author_id": author.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    db: Session = SessionLocal()
    author = get_author_by_id(db, request.email)
    if author and bcrypt.checkpw(request.password.encode('utf-8'), author.password.encode('utf-8')):
        return {"message": "Login realizado com sucesso!", "author_id": author.id}
    else:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
