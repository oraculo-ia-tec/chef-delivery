"""
Serviço de autenticação e autorização de usuários do Chef Delivery.

Utiliza bcrypt para hash e verificação de senhas.
"""

from __future__ import annotations

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.usuario import Usuario
from database.repositories import usuario_repo


# ── Hashing ────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Gera hash bcrypt a partir da senha em texto plano."""
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed.encode("utf-8")
    )


# ── Autenticação ───────────────────────────────────────────


async def authenticate_usuario(
    session: AsyncSession,
    email: str,
    password: str,
) -> Usuario | None:
    """
    Autentica um usuário por e-mail + senha.

    Retorna o objeto ``Usuario`` se válido, ou ``None`` se
    credenciais inválidas ou conta inativa.
    """
    usuario = await usuario_repo.get_usuario_by_email(session, email)
    if usuario is None:
        return None
    if not usuario.ativo:
        return None
    if not verify_password(password, usuario.senha_hash):
        return None
    return usuario


# ── Autorização ────────────────────────────────────────────


async def authorize_role(
    session: AsyncSession,
    usuario_id: int,
    roles_permitidos: list[str],
) -> bool:
    """
    Verifica se o usuário possui uma das roles permitidas.

    Retorna ``True`` se autorizado, ``False`` caso contrário.
    """
    usuario = await usuario_repo.get_usuario_by_id(session, usuario_id)
    if usuario is None or not usuario.ativo:
        return False
    return usuario.role in roles_permitidos


# ── Registro ───────────────────────────────────────────────


async def register_usuario(
    session: AsyncSession,
    *,
    nome: str,
    email: str,
    whatsapp: str,
    password: str,
    role: str = "cliente",
    imagem_perfil: str | None = None,
    **kwargs,
) -> Usuario:
    """
    Cria um novo usuário com senha hasheada.

    Aceita kwargs adicionais (endereco, cidade, cep, etc.)
    que são repassados ao repositório.
    """
    senha_hash = hash_password(password)
    return await usuario_repo.create_usuario(
        session,
        nome=nome,
        email=email,
        whatsapp=whatsapp,
        senha_hash=senha_hash,
        role=role,
        imagem_perfil=imagem_perfil,
        **kwargs,
    )
