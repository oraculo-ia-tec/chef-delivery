"""Repositório assíncrono de operações CRUD para Entregador."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.entregador import Entregador


async def create_entregador(
    session: AsyncSession,
    *,
    nome: str,
    email: str,
    whatsapp: str,
    modelo_moto: str | None = None,
    imagem_perfil: str | None = None,
    usuario_id: int | None = None,
) -> Entregador:
    entregador = Entregador(
        nome=nome,
        email=email,
        whatsapp=whatsapp,
        modelo_moto=modelo_moto,
        imagem_perfil=imagem_perfil,
        usuario_id=usuario_id,
    )
    session.add(entregador)
    await session.commit()
    await session.refresh(entregador)
    return entregador


async def get_entregador_by_id(
    session: AsyncSession, entregador_id: int,
) -> Entregador | None:
    result = await session.execute(
        select(Entregador).where(Entregador.id == entregador_id)
    )
    return result.scalar_one_or_none()


async def get_entregador_by_email(
    session: AsyncSession, email: str,
) -> Entregador | None:
    result = await session.execute(
        select(Entregador).where(Entregador.email == email)
    )
    return result.scalar_one_or_none()


async def list_entregadores(
    session: AsyncSession,
    *,
    status: str | None = None,
) -> list[Entregador]:
    stmt = select(Entregador)
    if status is not None:
        stmt = stmt.where(Entregador.status == status)
    stmt = stmt.order_by(Entregador.nome)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_entregador(
    session: AsyncSession,
    entregador_id: int,
    **kwargs,
) -> Entregador | None:
    entregador = await get_entregador_by_id(session, entregador_id)
    if entregador is None:
        return None
    for key, value in kwargs.items():
        if hasattr(entregador, key):
            setattr(entregador, key, value)
    await session.commit()
    await session.refresh(entregador)
    return entregador


async def delete_entregador(
    session: AsyncSession, entregador_id: int,
) -> bool:
    entregador = await get_entregador_by_id(session, entregador_id)
    if entregador is None:
        return False
    await session.delete(entregador)
    await session.commit()
    return True
