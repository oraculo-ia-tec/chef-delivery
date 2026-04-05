"""Repositório assíncrono de operações CRUD para Entrega."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.entrega import Entrega


async def create_entrega(
    session: AsyncSession,
    *,
    pedido_id: int,
    entregador_id: int,
    observacao: str | None = None,
) -> Entrega:
    entrega = Entrega(
        pedido_id=pedido_id,
        entregador_id=entregador_id,
        observacao=observacao,
    )
    session.add(entrega)
    await session.commit()
    await session.refresh(entrega)
    return entrega


async def get_entrega_by_id(
    session: AsyncSession, entrega_id: int,
) -> Entrega | None:
    result = await session.execute(
        select(Entrega).where(Entrega.id == entrega_id)
    )
    return result.scalar_one_or_none()


async def get_entrega_by_pedido(
    session: AsyncSession, pedido_id: int,
) -> Entrega | None:
    result = await session.execute(
        select(Entrega).where(Entrega.pedido_id == pedido_id)
    )
    return result.scalar_one_or_none()


async def update_entrega_status(
    session: AsyncSession,
    entrega_id: int,
    status: str,
    **kwargs,
) -> Entrega | None:
    entrega = await get_entrega_by_id(session, entrega_id)
    if entrega is None:
        return None
    entrega.status = status
    if status == "em_rota" and entrega.horario_saida is None:
        entrega.horario_saida = datetime.now(timezone.utc)
    elif status == "entregue" and entrega.horario_entrega is None:
        entrega.horario_entrega = datetime.now(timezone.utc)
    for key, value in kwargs.items():
        if hasattr(entrega, key):
            setattr(entrega, key, value)
    await session.commit()
    await session.refresh(entrega)
    return entrega


async def list_entregas_ativas(
    session: AsyncSession,
) -> list[Entrega]:
    stmt = (
        select(Entrega)
        .where(Entrega.status.in_(["atribuido", "em_rota"]))
        .order_by(Entrega.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_entregas_por_entregador(
    session: AsyncSession,
    entregador_id: int,
) -> list[Entrega]:
    stmt = (
        select(Entrega)
        .where(Entrega.entregador_id == entregador_id)
        .order_by(Entrega.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
