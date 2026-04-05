"""
Módulo de conexão assíncrona com o banco de dados Chef Delivery.

Utiliza SQLAlchemy AsyncIO + aiosqlite para operações não-bloqueantes.
O banco SQLite é criado como ``chef_delivery.db`` na raiz do projeto.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models.model_base import ModelBase


_DATABASE_URL = "sqlite+aiosqlite:///chef_delivery.db"

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Retorna (ou cria) a engine assíncrona singleton."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _DATABASE_URL,
            echo=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Retorna (ou cria) a fábrica de sessões assíncronas."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Gerador assíncrono de sessão – ideal para uso com ``async for``
    ou como dependency injection.
    """
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def create_session() -> AsyncSession:
    """Cria e devolve uma sessão avulsa (o chamador deve fechar)."""
    factory = get_session_factory()
    return factory()


async def create_tables() -> None:
    """Cria todas as tabelas registradas no ModelBase.metadata."""
    import database.models.__all_models  # noqa: F401 – registra os modelos

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

    print("✅ Tabelas criadas com sucesso no chef_delivery.db!")
    for name in ModelBase.metadata.tables:
        print(f"   • {name}")


async def drop_tables() -> None:
    """Remove todas as tabelas (CUIDADO – uso em testes)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
