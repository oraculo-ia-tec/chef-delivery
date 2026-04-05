"""Repositório assíncrono de operações CRUD para Pagamento."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pagamento import Pagamento


async def create_pagamento(
    session: AsyncSession,
    *,
    pedido_id: int,
    usuario_id: int,
    valor: Decimal | float,
    metodo_pagamento: str,
    asaas_payment_id: str | None = None,
    pix_payload: str | None = None,
    pix_qr_code_base64: str | None = None,
    pix_expiration_date: datetime | None = None,
    invoice_url: str | None = None,
) -> Pagamento:
    pagamento = Pagamento(
        pedido_id=pedido_id,
        usuario_id=usuario_id,
        valor=valor,
        metodo_pagamento=metodo_pagamento,
        asaas_payment_id=asaas_payment_id,
        pix_payload=pix_payload,
        pix_qr_code_base64=pix_qr_code_base64,
        pix_expiration_date=pix_expiration_date,
        invoice_url=invoice_url,
    )
    session.add(pagamento)
    await session.commit()
    await session.refresh(pagamento)
    return pagamento


async def get_pagamento_by_id(
    session: AsyncSession, pagamento_id: int,
) -> Pagamento | None:
    result = await session.execute(
        select(Pagamento).where(Pagamento.id == pagamento_id)
    )
    return result.scalar_one_or_none()


async def get_pagamento_by_pedido(
    session: AsyncSession, pedido_id: int,
) -> Pagamento | None:
    result = await session.execute(
        select(Pagamento).where(Pagamento.pedido_id == pedido_id)
    )
    return result.scalar_one_or_none()


async def get_pagamento_by_asaas_id(
    session: AsyncSession, asaas_payment_id: str,
) -> Pagamento | None:
    result = await session.execute(
        select(Pagamento).where(
            Pagamento.asaas_payment_id == asaas_payment_id
        )
    )
    return result.scalar_one_or_none()


async def update_pagamento_status(
    session: AsyncSession,
    pagamento_id: int,
    status: str,
    **kwargs,
) -> Pagamento | None:
    pagamento = await get_pagamento_by_id(session, pagamento_id)
    if pagamento is None:
        return None
    pagamento.status = status
    if status == "confirmado" and pagamento.data_confirmacao is None:
        pagamento.data_confirmacao = datetime.now(timezone.utc)
    for key, value in kwargs.items():
        if hasattr(pagamento, key):
            setattr(pagamento, key, value)
    await session.commit()
    await session.refresh(pagamento)
    return pagamento


async def list_pagamentos(
    session: AsyncSession,
    *,
    usuario_id: int | None = None,
    status: str | None = None,
) -> list[Pagamento]:
    stmt = select(Pagamento)
    if usuario_id is not None:
        stmt = stmt.where(Pagamento.usuario_id == usuario_id)
    if status is not None:
        stmt = stmt.where(Pagamento.status == status)
    stmt = stmt.order_by(Pagamento.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())
