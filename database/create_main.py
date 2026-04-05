"""
Script para criação das tabelas do banco de dados Chef Delivery.

Uso:
    python -m database.create_tables
"""

import asyncio
from database.config.connection import create_tables


async def main():
    print("🔄 Criando tabelas do Chef Delivery...")
    await create_tables()
    print("🎉 Banco chef_delivery.db pronto para uso!")


if __name__ == "__main__":
    asyncio.run(main())
