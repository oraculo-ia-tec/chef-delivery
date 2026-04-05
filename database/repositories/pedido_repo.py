"""Repositório assíncrono de operações CRUD para Pedido e ItemPedido."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.pedido import Pedido
from database.models.item_pedido import ItemPedido


async def create_pedido(
    session: AsyncSession,
    *,
    codigo: str,
    usuario_id: int,
    endereco_entrega: str,
    valor_total: Decimal | float,
    observacao: str | None = None,
    status: str = "aguardando_pagamento",
) -> Pedido:
    pedido = Pedido(
        codigo=codigo,
        usuario_id=usuario_id,
        endereco_entrega=endereco_entrega,
        valor_total=valor_total,
        observacao=observacao,
        status=status,
    )
    session.add(pedido)
    await session.commit()
    await session.refresh(pedido)
    return pedido


async def get_pedido_by_id(
    session: AsyncSession,
    pedido_id: int,
    *,
    load_itens: bool = False,
) -> Pedido | None:
    stmt = select(Pedido).where(Pedido.id == pedido_id)
    if load_itens:
        stmt = stmt.options(selectinload(Pedido.itens))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_pedido_by_codigo(
    session: AsyncSession,
    codigo: str,
    *,
    load_itens: bool = False,
) -> Pedido | None:
    stmt = select(Pedido).where(Pedido.codigo == codigo)
    if load_itens:
        stmt = stmt.options(selectinload(Pedido.itens))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_pedidos(
    session: AsyncSession,
    *,
    usuario_id: int | None = None,
    status: str | None = None,
) -> list[Pedido]:
    stmt = select(Pedido)
    if usuario_id is not None:
        stmt = stmt.where(Pedido.usuario_id == usuario_id)
    if status is not None:
        stmt = stmt.where(Pedido.status == status)
    stmt = stmt.order_by(Pedido.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_pedido_status(
    session: AsyncSession,
    pedido_id: int,
    status: str,
    **kwargs,
) -> Pedido | None:
    pedido = await get_pedido_by_id(session, pedido_id)
    if pedido is None:
        return None
    pedido.status = status
    for key, value in kwargs.items():
        if hasattr(pedido, key):
            setattr(pedido, key, value)
    await session.commit()
    await session.refresh(pedido)
    return pedido


async def add_item_pedido(
    session: AsyncSession,
    *,
    pedido_id: int,
    produto_id: int,
    quantidade: Decimal | float,
    preco_unitario: Decimal | float,
) -> ItemPedido:
    subtotal = Decimal(str(quantidade)) * Decimal(str(preco_unitario))
    item = ItemPedido(
        pedido_id=pedido_id,
        produto_id=produto_id,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        subtotal=subtotal,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def list_itens_pedido(
    session: AsyncSession,
    pedido_id: int,
) -> list[ItemPedido]:
    stmt = (
        select(ItemPedido)
        .where(ItemPedido.pedido_id == pedido_id)
        .order_by(ItemPedido.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
