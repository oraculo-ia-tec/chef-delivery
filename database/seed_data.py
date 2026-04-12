"""
Script para popular o banco Chef Delivery com categorias e produtos
baseado no catálogo de ``pgs/produtos.py``.

Uso:
    python -m database.seed_data
"""

from __future__ import annotations

import asyncio

from database.config.connection import create_tables, create_session
from database.repositories.produto_repo import (
    create_categoria,
    create_produto,
    get_categoria_by_nome,
)
from database.repositories import usuario_repo
from database.services.auth_service import hash_password


# ── Usuários padrão do sistema ─────────────────────────────

USUARIOS_SEED: list[dict] = [
    {
        "nome": "William Eustáquio Gomes da Silva",
        "email": "oraculoiatec@gmail.com",
        "whatsapp": "998417976",
        "senha": "william2026",
        "role": "admin",
        "email_verificado": True,
    },
    {
        "nome": "Admin Chef",
        "email": "admin@chef.com",
        "whatsapp": "31999990000",
        "senha": "Chef@2025",
        "role": "admin",
        "email_verificado": True,
    },
]


# ── Catálogo completo do Chef Delivery ─────────────────────

CATEGORIAS_SEED: dict[str, dict] = {
    "Boi": {
        "icone": "🥩",
        "unidade": "kg",
        "itens": {
            "Alcatra (peça)": 32.99, "Alcatra (kg)": 36.99,
            "Contra filé (peça)": 34.99, "Contra filé (kg)": 37.99,
            "Chã de dentro (peça)": 28.99, "Chã de dentro (kg)": 33.99,
            "Chã de fora (peça)": 29.99, "Chã de fora (kg)": 33.99,
            "Patinho (peça)": 27.99, "Patinho (kg)": 33.99,
            "Pá completa (peça)": 24.99,
            "Miolo de acém (peça)": 24.99, "Miolo de acém (kg)": 29.99,
            "Maçã de peito (peça)": 24.99, "Maçã de peito (kg)": 29.99,
            "Picanha Premiata": 79.99, "Picanha Dia a Dia": 49.99,
            "Filé Mignon c/ cordão": 49.99, "Maminha": 37.99,
            "Miolo de alcatra": 39.99, "Lagarto": 33.99,
            "Lagarto recheado": 34.99, "Lagartinho": 33.99,
            "Garrão": 29.99, "Acém": 24.99,
            "Pá/Paleta": 29.99, "Capa de filé": 29.99,
            "Músculo dianteiro": 29.99, "Músculo traseiro": 29.99,
            "Fraldinha": 34.99, "Fraldão": 39.99,
            "Cupim": 35.99, "Costelão inteiro": 24.99,
            "Costela de boi": 19.99, "Costela gaúcha": 19.99,
            "Costelão especial": 21.99, "Costela recheada": 34.99,
            "Costela desossada": 49.99, "Carne de sol 2ª": 34.99,
            "Chãzinha": 29.99, "Rabada": 35.99,
            "Dobradinha": 15.99, "Dobradinha colméia": 24.99,
            "Fígado (bife)": 14.99, "Língua de boi": 16.99,
            "Coração de boi": 9.99, "Mocotó": 10.99,
            "Moída promoção": 19.99, "Acém promocional": 19.99,
        },
    },
    "Porco": {
        "icone": "🐷",
        "unidade": "kg",
        "itens": {
            "Bisteca": 16.99, "Tomahawk suíno": 21.99,
            "Pazinha PC": 15.99, "Pazinha": 16.99,
            "Pazinha pele e osso": 14.99, "Pazinha pele s/ osso": 15.99,
            "Pazinha defumada": 29.99,
            "Pernil PC": 16.99, "Pernil": 18.99,
            "Pernil recheado": 21.99,
            "Lombo PC": 18.99, "Lombo": 19.99,
            "Lombo com pele": 18.99, "Lombo defumado": 29.99,
            "Lombo recheado": 23.99, "Copa lombo": 21.99,
            "Lombinho": 21.99, "Picanha suína": 26.99,
            "Costelinha c/ lombo": 20.99, "Costelinha aparada": 24.99,
            "Costelinha defumada": 34.99, "Rabinho": 21.99,
            "Orelha": 9.99, "Pé de porco": 9.99,
            "Rabo de porco": 14.99, "Toucinho": 12.99,
            "Bacon": 29.99,
        },
    },
    "Frango": {
        "icone": "🍗",
        "unidade": "kg",
        "itens": {
            "Frango inteiro": 12.99, "Frango em pedaços": 14.99,
            "Peito de frango": 16.99, "Filé de peito": 19.99,
            "Coxa e sobrecoxa": 13.99, "Coxa": 12.99,
            "Sobrecoxa": 14.99, "Sobrecoxa desossada": 17.99,
            "Asa de frango": 14.99, "Coxinha da asa": 16.99,
            "Meio da asa": 14.99, "Dorso/Carcaça": 6.99,
            "Pé de frango": 5.99, "Moela": 12.99,
            "Coração de frango": 14.99, "Fígado de frango": 9.99,
        },
    },
    "Linguiça": {
        "icone": "🌭",
        "unidade": "kg",
        "itens": {
            "Linguiça caseira": 19.99, "Linguiça toscana": 21.99,
            "Linguiça calabresa": 24.99, "Linguiça de frango": 16.99,
            "Linguiça mista": 18.99, "Linguiça apimentada": 22.99,
            "Linguiça cuiabana": 21.99,
        },
    },
    "Peixe": {
        "icone": "🐟",
        "unidade": "kg",
        "itens": {
            "Tilápia inteira": 16.99, "Filé de tilápia": 29.99,
            "Sardinha": 9.99, "Merluza": 24.99,
            "Salmão (kg)": 59.99, "Camarão limpo": 49.99,
        },
    },
    "Kits": {
        "icone": "📦",
        "unidade": "un",
        "itens": {
            "Kit Básico": 89.99, "Kit Família": 129.99,
            "Kit Churrasco": 149.99, "Kit Gold": 199.99,
            "Kit Premium": 249.99,
        },
    },
    "Bebidas": {
        "icone": "🥤",
        "unidade": "un",
        "itens": {
            "Coca-Cola 2L": 10.99, "Guaraná 2L": 8.99,
            "Água mineral 500ml": 2.99, "Cerveja lata": 4.99,
            "Suco natural 1L": 12.99,
        },
    },
    "Acompanhamentos": {
        "icone": "🧂",
        "unidade": "un",
        "itens": {
            "Carvão 3kg": 18.99, "Carvão 5kg": 27.99,
            "Sal grosso 1kg": 3.99, "Farofa pronta 500g": 7.99,
            "Vinagrete pronto": 9.99, "Pão de alho (6un)": 14.99,
            "Queijo coalho (espeto)": 5.99,
        },
    },
}


async def seed_usuarios():
    """Cria usuários padrão se não existirem."""
    session = await create_session()
    try:
        total_usuarios = 0
        for user_data in USUARIOS_SEED:
            existing = await usuario_repo.get_usuario_by_email(session, user_data["email"])
            if existing:
                print(f"  ⏭️  Usuário '{user_data['email']}' já existe (id={existing.id})")
            else:
                senha_hash = hash_password(user_data["senha"])
                novo_user = await usuario_repo.create_usuario(
                    session,
                    nome=user_data["nome"],
                    email=user_data["email"],
                    whatsapp=user_data["whatsapp"],
                    senha_hash=senha_hash,
                    role=user_data["role"],
                )
                if user_data.get("email_verificado"):
                    await usuario_repo.update_usuario(session, novo_user.id, email_verificado=True)
                total_usuarios += 1
                print(f"  ✅ Usuário '{user_data['email']}' criado (id={novo_user.id})")
        return total_usuarios
    finally:
        await session.close()


async def seed_all():
    """Cria tabelas (se necessário) e popula categorias + produtos + usuários."""
    await create_tables()
    
    # Seed de usuários primeiro
    print("\n👤 Criando usuários padrão...")
    total_usuarios = await seed_usuarios()

    session = await create_session()
    try:
        total_categorias = 0
        total_produtos = 0

        for cat_nome, cat_data in CATEGORIAS_SEED.items():
            # Evita duplicatas
            existing = await get_categoria_by_nome(session, cat_nome)
            if existing:
                cat_id = existing.id
                print(f"  ⏭️  Categoria '{cat_nome}' já existe (id={cat_id})")
            else:
                cat = await create_categoria(
                    session,
                    nome=cat_nome,
                    icone=cat_data.get("icone"),
                    unidade_padrao=cat_data.get("unidade", "kg"),
                )
                cat_id = cat.id
                total_categorias += 1
                print(f"  ✅ Categoria '{cat_nome}' criada (id={cat_id})")

            unidade = cat_data.get("unidade", "kg")
            for prod_nome, preco in cat_data.get("itens", {}).items():
                try:
                    await create_produto(
                        session,
                        categoria_id=cat_id,
                        nome=prod_nome,
                        preco=preco,
                        unidade=unidade,
                    )
                    total_produtos += 1
                except Exception:
                    # Produto já existe (constraint unique)
                    await session.rollback()
                    session = await create_session()

        print(f"\n📊 Seed concluído: {total_usuarios} usuários, {total_categorias} categorias, "
              f"{total_produtos} produtos inseridos.")
    finally:
        await session.close()


if __name__ == "__main__":
    print("🌱 Populando banco Chef Delivery...")
    asyncio.run(seed_all())
