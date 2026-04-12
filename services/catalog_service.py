from typing import Any, Dict, List, Optional


class CatalogService:
    def __init__(self):
        self.catalog = {
            "carnes": {
                "picanha": [
                    {"nome": "Picanha Tradicional (Zebuína/Nelore)",
                     "preco": 79.99, "unidade": "kg"},
                    {"nome": "Picanha Angus (Premium)",
                     "preco": 89.99, "unidade": "kg"},
                    {"nome": "Picanha Wagyu", "preco": 189.99, "unidade": "kg"},
                    {"nome": "Picanha Argentina ou Uruguaia",
                        "preco": 119.99, "unidade": "kg"},
                    {"nome": "Picanha de Cordeiro",
                        "preco": 99.99, "unidade": "kg"},
                    {"nome": "Picanha Suína", "preco": 26.99, "unidade": "kg"},
                ],
                "costela": [
                    {"nome": "Costela de Boi", "preco": 19.99, "unidade": "kg"},
                    {"nome": "Costela Gaúcha", "preco": 19.99, "unidade": "kg"},
                    {"nome": "Costelão Especial", "preco": 21.99, "unidade": "kg"},
                    {"nome": "Costela Recheada", "preco": 34.99, "unidade": "kg"},
                    {"nome": "Costela Desossada", "preco": 49.99, "unidade": "kg"},
                ],
                "peixe": [
                    {"nome": "Cavalinha", "preco": 10.99, "unidade": "kg"},
                    {"nome": "Sardinha", "preco": 14.99, "unidade": "kg"},
                    {"nome": "Filé de Merluza", "preco": 39.99, "unidade": "kg"},
                    {"nome": "Cascudo", "preco": 17.99, "unidade": "kg"},
                    {"nome": "Filé de Tilápia", "preco": 49.99, "unidade": "kg"},
                ],
                "frango": [
                    {"nome": "Coxa e Sobrecoxa", "preco": 9.99, "unidade": "kg"},
                    {"nome": "Peito de Frango", "preco": 14.99, "unidade": "kg"},
                    {"nome": "Asa de Frango", "preco": 14.99, "unidade": "kg"},
                    {"nome": "Frango Resfriado", "preco": 10.99, "unidade": "kg"},
                ],
            },
            "bebidas": {
                "refrigerantes": [
                    {"nome": "Coca-Cola 350ml", "preco": 4.99, "unidade": "un"},
                    {"nome": "Fanta 350ml", "preco": 4.99, "unidade": "un"},
                    {"nome": "Coca Zero 600ml", "preco": 6.99, "unidade": "un"},
                    {"nome": "Fanta PET 2L", "preco": 7.50, "unidade": "un"},
                ],
                "sucos": [
                    {"nome": "Suco Del Valle 290ml",
                        "preco": 4.99, "unidade": "un"},
                    {"nome": "Powerade", "preco": 4.99, "unidade": "un"},
                ],
                "aguas": [
                    {"nome": "Água sem gás 500ml", "preco": 3.00, "unidade": "un"},
                    {"nome": "Água com gás 500ml", "preco": 3.00, "unidade": "un"},
                ],
            },
        }

    def list_main_categories(self) -> List[str]:
        return ["Carnes", "Bebidas"]

    def list_meat_categories(self) -> List[str]:
        return ["Picanha", "Costela", "Peixe", "Frango"]

    def list_drink_categories(self) -> List[str]:
        return ["Refrigerantes", "Sucos", "Águas"]

    def get_models_by_category(self, group: str, category: str) -> List[Dict[str, Any]]:
        group_key = group.lower()
        category_key = category.lower()
        return self.catalog.get(group_key, {}).get(category_key, [])

    def find_group_or_category_from_text(self, text: str) -> Dict[str, Optional[str]]:
        t = text.lower().strip()

        if "bebida" in t or "refrigerante" in t or "suco" in t or "água" in t or "agua" in t:
            return {"group": "bebidas", "category": None}

        if "carne" in t:
            return {"group": "carnes", "category": None}

        if "picanha" in t:
            return {"group": "carnes", "category": "picanha"}

        if "costela" in t:
            return {"group": "carnes", "category": "costela"}

        if "peixe" in t or "tilápia" in t or "tilapia" in t or "sardinha" in t or "merluza" in t:
            return {"group": "carnes", "category": "peixe"}

        if "frango" in t or "coxa" in t or "asa" in t or "sobrecoxa" in t:
            return {"group": "carnes", "category": "frango"}

        return {"group": None, "category": None}

    def find_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        wanted = product_name.lower().strip()
        for group_data in self.catalog.values():
            for category_models in group_data.values():
                for product in category_models:
                    if product["nome"].lower() == wanted:
                        return product
        return None

    def find_product_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        t = text.lower().strip()
        for group_data in self.catalog.values():
            for category_models in group_data.values():
                for product in category_models:
                    if product["nome"].lower() in t:
                        return product
        return None
