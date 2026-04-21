"""Repositório assíncrono de operações CRUD paraUsuário."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.usuario import Usuario


async def create_usuario(
    session: AsyncSession,
    *,
    nome: str,
    email: str,
    whatsapp: str,
    senha_hash: str,
    role: str = "cliente",
    cpf_cnpj: str | None = None,
    imagem_perfil: str | None = None,
    endereco: str | None = None,
    numero: str | None = None,
    complemento: str | None = None,
    bairro: str | None = None,
    cidade: str | None = None,
    cep: str | None = None,
) -> Usuario:
    usuario = Usuario(
        nome=nome,
        email=email,
        whatsapp=whatsapp,
        senha_hash=senha_hash,
        role=role,
        cpf_cnpj=cpf_cnpj,
        imagem_perfil=imagem_perfil,
        endereco=endereco,
        numero=numero,
        complemento=complemento,
        bairro=bairro,
        cidade=cidade,
        cep=cep,
    )
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario


async def get_usuario_by_id(
    session: AsyncSession, usuario_id: int,
) -> Usuario | None:
    result = await session.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    return result.scalar_one_or_none()


async def get_usuario_by_email(
    session: AsyncSession, email: str,
) -> Usuario | None:
    result = await session.execute(
        select(Usuario).where(Usuario.email == email)
    )
    return result.scalar_one_or_none()


async def get_usuario_by_whatsapp(
    session: AsyncSession, whatsapp: str,
) -> Usuario | None:
    result = await session.execute(
        select(Usuario).where(Usuario.whatsapp == whatsapp)
    )
    return result.scalar_one_or_none()


async def get_usuario_by_asaas_id(
    session: AsyncSession, asaas_customer_id: str,
) -> Usuario | None:
    """Busca usuário pelo ID do cliente no Asaas."""
    result = await session.execute(
        select(Usuario).where(Usuario.asaas_customer_id == asaas_customer_id)
    )
    return result.scalar_one_or_none()


async def get_usuario_by_cpf_cnpj(
    session: AsyncSession, cpf_cnpj: str,
) -> Usuario | None:
    """Busca usuário pelo CPF/CNPJ."""
    result = await session.execute(
        select(Usuario).where(Usuario.cpf_cnpj == cpf_cnpj)
    )
    return result.scalar_one_or_none()


async def list_clientes(
    session: AsyncSession,
    *,
    ativo: bool | None = None,
    com_asaas: bool | None = None,
) -> list[Usuario]:
    """Lista apenas usuários com role='cliente'."""
    stmt = select(Usuario).where(Usuario.role == "cliente")
    if ativo is not None:
        stmt = stmt.where(Usuario.ativo == ativo)
    if com_asaas is True:
        stmt = stmt.where(Usuario.asaas_customer_id.isnot(None))
    elif com_asaas is False:
        stmt = stmt.where(Usuario.asaas_customer_id.is_(None))
    stmt = stmt.order_by(Usuario.nome)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_usuarios(
    session: AsyncSession,
    *,
    role: str | None = None,
    ativo: bool | None = None,
) -> list[Usuario]:
    stmt = select(Usuario)
    if role is not None:
        stmt = stmt.where(Usuario.role == role)
    if ativo is not None:
        stmt = stmt.where(Usuario.ativo == ativo)
    stmt = stmt.order_by(Usuario.nome)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_usuario(
    session: AsyncSession,
    usuario_id: int,
    **kwargs,
) -> Usuario | None:
    usuario = await get_usuario_by_id(session, usuario_id)
    if usuario is None:
        return None
    for key, value in kwargs.items():
        if hasattr(usuario, key):
            setattr(usuario, key, value)
    await session.commit()
    await session.refresh(usuario)
    return usuario


async def delete_usuario(
    session: AsyncSession, usuario_id: int,
) -> bool:
    usuario = await get_usuario_by_id(session, usuario_id)
    if usuario is None:
        return False
    await session.delete(usuario)
    await session.commit()
    return True
