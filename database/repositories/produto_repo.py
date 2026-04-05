"""Repositório assíncrono de operações CRUD para Categoria e Produto."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.categoria import Categoria
from database.models.produto import Produto


# ── Categoria ──────────────────────────────────────────────


async def create_categoria(
    session: AsyncSession,
    *,
    nome: str,
    icone: str | None = None,
    unidade_padrao: str = "kg",
) -> Categoria:
    categoria = Categoria(
        nome=nome, icone=icone, unidade_padrao=unidade_padrao,
    )
    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)
    return categoria


async def get_categoria_by_id(
    session: AsyncSession, categoria_id: int,
) -> Categoria | None:
    result = await session.execute(
        select(Categoria).where(Categoria.id == categoria_id)
    )
    return result.scalar_one_or_none()


async def get_categoria_by_nome(
    session: AsyncSession, nome: str,
) -> Categoria | None:
    result = await session.execute(
        select(Categoria).where(Categoria.nome == nome)
    )
    return result.scalar_one_or_none()


async def list_categorias(
    session: AsyncSession, *, ativo: bool = True,
) -> list[Categoria]:
    stmt = (
        select(Categoria)
        .where(Categoria.ativo == ativo)
        .order_by(Categoria.nome)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# ── Produto ────────────────────────────────────────────────


async def create_produto(
    session: AsyncSession,
    *,
    categoria_id: int,
    nome: str,
    preco: Decimal | float,
    unidade: str = "kg",
) -> Produto:
    produto = Produto(
        categoria_id=categoria_id,
        nome=nome,
        preco=preco,
        unidade=unidade,
    )
    session.add(produto)
    await session.commit()
    await session.refresh(produto)
    return produto


async def get_produto_by_id(
    session: AsyncSession, produto_id: int,
) -> Produto | None:
    result = await session.execute(
        select(Produto).where(Produto.id == produto_id)
    )
    return result.scalar_one_or_none()


async def list_produtos(
    session: AsyncSession,
    *,
    categoria_id: int | None = None,
    ativo: bool = True,
) -> list[Produto]:
    stmt = select(Produto).where(Produto.ativo == ativo)
    if categoria_id is not None:
        stmt = stmt.where(Produto.categoria_id == categoria_id)
    stmt = stmt.order_by(Produto.nome)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_produto(
    session: AsyncSession,
    produto_id: int,
    **kwargs,
) -> Produto | None:
    produto = await get_produto_by_id(session, produto_id)
    if produto is None:
        return None
    for key, value in kwargs.items():
        if hasattr(produto, key):
            setattr(produto, key, value)
    await session.commit()
    await session.refresh(produto)
    return produto
