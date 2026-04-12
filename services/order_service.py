from typing import Dict, List


class OrderService:
    @staticmethod
    def add_item(cart: List[Dict], product: Dict, quantity: float) -> Dict:
        subtotal = round(product["preco"] * quantity, 2)
        item = {
            "nome": product["nome"],
            "preco": float(product["preco"]),
            "quantidade": float(quantity) if product["unidade"] == "kg" else int(quantity),
            "unidade": product["unidade"],
            "subtotal": subtotal,
        }
        cart.append(item)
        return item

    @staticmethod
    def get_total(cart: List[Dict]) -> float:
        return round(sum(item["subtotal"] for item in cart), 2)

    @staticmethod
    def summarize_cart(cart: List[Dict]) -> List[str]:
        lines = []
        for item in cart:
            qty = f"{item['quantidade']:.2f}" if item[
                "unidade"] == "kg" else f"{int(item['quantidade'])}"
            unidade = "kg" if item["unidade"] == "kg" else "un"
            lines.append(
                f"- {item['nome']} | {qty} {unidade} | R$ {item['subtotal']:.2f}")
        return lines
