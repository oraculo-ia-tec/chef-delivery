from __future__ import annotations

import asyncio
import json
import os
from datetime import date, timedelta
from typing import Any

from api_asaas import (
    ChefDeliveryAsaasService,
    InMemoryPaymentRepository,
    build_asaas_client,
    create_payment_from_streamlit_session,
    handle_asaas_webhook_payload,
    build_test_order_examples,
)

ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_ENVIRONMENT = os.getenv("ASAAS_ENVIRONMENT", "sandbox")

_repository = InMemoryPaymentRepository()


class MCPServerError(Exception):
    pass


async def _build_service() -> ChefDeliveryAsaasService:
    if not ASAAS_API_KEY:
        raise MCPServerError("ASAAS_API_KEY não configurada")
    client = await build_asaas_client(api_key=ASAAS_API_KEY, environment=ASAAS_ENVIRONMENT)
    return ChefDeliveryAsaasService(client, repository=_repository)


async def mcp_create_order_payment(payload: dict[str, Any]) -> dict[str, Any]:
    required = ["name", "endereco", "whatsapp",
                "pedido_texto", "total_value", "payment_method"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise MCPServerError(
            "Campos obrigatórios ausentes: " + ", ".join(missing))

    session_state = {
        "name": payload.get("name"),
        "primeiro_nome": str(payload.get("name", "")).split()[0] if payload.get("name") else "",
        "endereco": payload.get("endereco"),
        "whatsapp": payload.get("whatsapp"),
        "pedido": payload.get("pedido") or [],
        "pedido_texto": payload.get("pedido_texto"),
        "observacao": payload.get("observacao") or "",
        "total_value": payload.get("total_value"),
        "username": payload.get("username") or payload.get("name"),
        "email": payload.get("email") or "",
        "cpf_cnpj": payload.get("cpf_cnpj") or "",
        "postal_code": payload.get("postal_code") or "",
        "address_number": payload.get("address_number") or "S/N",
        "province": payload.get("province") or "",
        "remote_ip": payload.get("remote_ip") or "127.0.0.1",
    }

    service = await _build_service()
    async with service.client:
        result = await create_payment_from_streamlit_session(
            service,
            session_state,
            due_date=payload.get("due_date") or (
                date.today() + timedelta(days=1)).isoformat(),
            order_id=payload.get(
                "order_id") or f"PED-MCP-{date.today().strftime('%Y%m%d')}-001",
            total_value=payload.get("total_value"),
            payment_method=payload.get("payment_method"),
            email=payload.get("email"),
            cpf_cnpj=payload.get("cpf_cnpj"),
            postal_code=payload.get("postal_code"),
            address_number=payload.get("address_number"),
            province=payload.get("province"),
            remote_ip=payload.get("remote_ip") or "127.0.0.1",
        )
        return result


async def mcp_get_order_payment_status(payload: dict[str, Any]) -> dict[str, Any]:
    payment_id = payload.get("payment_id")
    if not payment_id:
        raise MCPServerError("payment_id é obrigatório")
    service = await _build_service()
    async with service.client:
        return await service.get_order_payment_status(payment_id)


async def mcp_handle_asaas_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    service = await _build_service()
    return await service.handle_webhook(payload)


async def mcp_list_test_order_examples(_: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"examples": build_test_order_examples()}


TOOLS = {
    "create_order_payment": {
        "description": "Cria cobrança Asaas para um pedido do Chef Delivery via Pix, boleto ou checkout de cartão.",
        "handler": mcp_create_order_payment,
    },
    "get_order_payment_status": {
        "description": "Consulta status de um pagamento Asaas pelo payment_id.",
        "handler": mcp_get_order_payment_status,
    },
    "handle_asaas_webhook_payload": {
        "description": "Processa payload de webhook Asaas e atualiza o estado local do pagamento.",
        "handler": mcp_handle_asaas_webhook_payload,
    },
    "list_test_order_examples": {
        "description": "Lista cenários reais de teste com base no catálogo do Chef Delivery.",
        "handler": mcp_list_test_order_examples,
    },
}


async def dispatch(message: dict[str, Any]) -> dict[str, Any]:
    tool_name = message.get("tool")
    payload = message.get("payload") or {}
    if tool_name not in TOOLS:
        raise MCPServerError(f"Ferramenta não encontrada: {tool_name}")
    handler = TOOLS[tool_name]["handler"]
    data = await handler(payload)
    return {
        "ok": True,
        "tool": tool_name,
        "data": data,
    }


async def stdin_server() -> None:
    while True:
        line = input()
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            response = await dispatch(message)
        except Exception as exc:
            response = {"ok": False, "error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    asyncio.run(stdin_server())
