"""
Serviço de processamento de webhooks de pagamento do ASAAS.

Fluxo principal:
    1. Recebe payload do webhook ASAAS
    2. Verifica assinatura (HMAC-SHA256 com WEBHOOK_PAY_ASAAS)
    3. Registra na tabela webhook_logs
    4. Localiza o pagamento pelo asaas_payment_id
    5. Atualiza pagamento.status e pedido.status conforme evento
    6. Quando confirmado: pedido.status → "pago" → inicia preparação
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.webhook_log import WebhookLog
from database.repositories import pagamento_repo, pedido_repo


# ── Eventos ASAAS ──────────────────────────────────────────

PAYMENT_CONFIRMED_EVENTS = frozenset({
    "PAYMENT_CONFIRMED",
    "PAYMENT_RECEIVED",
    "CHECKOUT_PAID",
})

PAYMENT_FAILED_EVENTS = frozenset({
    "PAYMENT_REPROVED_BY_RISK_ANALYSIS",
    "PAYMENT_CREDIT_CARD_CAPTURE_REFUSED",
    "PAYMENT_DELETED",
    "PAYMENT_REFUNDED",
    "PAYMENT_CHARGEBACK_REQUESTED",
    "CHECKOUT_CANCELED",
    "CHECKOUT_EXPIRED",
})


# ── Verificação de assinatura ──────────────────────────────


def verify_webhook_signature(
    payload_body: bytes,
    signature: str,
    webhook_secret: str,
) -> bool:
    """
    Verifica assinatura HMAC-SHA256 do webhook ASAAS.

    Args:
        payload_body: Corpo bruto da requisição (bytes).
        signature: Valor do header de assinatura.
        webhook_secret: Chave WEBHOOK_PAY_ASAAS do .env.
    """
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ── Processamento do webhook ───────────────────────────────


async def process_payment_webhook(
    session: AsyncSession,
    payload: dict,
) -> dict:
    """
    Processa payload de webhook de pagamento do ASAAS.

    Fluxo:
        1. Loga o evento (webhook_logs)
        2. Busca pagamento pelo asaas_payment_id
        3. Se PAYMENT_CONFIRMED → pagamento.status='confirmado',
           pedido.status='pago', pedido.horario_chegada=now
        4. Se PAYMENT_FAILED → pagamento.status='recusado',
           pedido.status='cancelado'

    Retorna dict com informações da ação executada.
    """
    event_name = payload.get("event", "")
    payment_data = payload.get("payment") or {}
    asaas_payment_id = payment_data.get("id")

    # 1. Registrar log do webhook
    log = WebhookLog(
        event_id=payload.get("id"),
        event_type=event_name,
        asaas_payment_id=asaas_payment_id,
        payload=json.dumps(payload, default=str),
    )
    session.add(log)

    result = {
        "event": event_name,
        "asaas_payment_id": asaas_payment_id,
        "action": "nenhuma",
        "success": False,
    }

    if not asaas_payment_id:
        log.resultado = "payment_id ausente no payload"
        await session.commit()
        return result

    # 2. Localizar pagamento no banco
    pagamento = await pagamento_repo.get_pagamento_by_asaas_id(
        session, asaas_payment_id
    )
    if pagamento is None:
        log.resultado = f"pagamento não encontrado: {asaas_payment_id}"
        await session.commit()
        return result

    # 3. Processar conforme tipo de evento
    if event_name in PAYMENT_CONFIRMED_EVENTS:
        # ── Pagamento confirmado → iniciar preparação ──
        pagamento.status = "confirmado"
        pagamento.data_confirmacao = datetime.now(timezone.utc)
        pagamento.webhook_event = event_name

        pedido = await pedido_repo.get_pedido_by_id(
            session, pagamento.pedido_id
        )
        if pedido:
            pedido.status = "pago"
            pedido.horario_chegada = datetime.now(timezone.utc)

        result["action"] = "pagamento_confirmado"
        result["success"] = True
        log.processado = True
        log.resultado = (
            "pagamento confirmado, pedido movido para preparação"
        )

    elif event_name in PAYMENT_FAILED_EVENTS:
        # ── Pagamento recusado → cancelar pedido ──
        pagamento.status = "recusado"
        pagamento.webhook_event = event_name

        pedido = await pedido_repo.get_pedido_by_id(
            session, pagamento.pedido_id
        )
        if pedido:
            pedido.status = "cancelado"

        result["action"] = "pagamento_recusado"
        result["success"] = True
        log.processado = True
        log.resultado = f"pagamento recusado: {event_name}"

    else:
        # ── Outros eventos (ex: PAYMENT_UPDATED) ──
        pagamento.webhook_event = event_name
        log.processado = True
        log.resultado = f"evento registrado: {event_name}"
        result["action"] = "evento_registrado"
        result["success"] = True

    await session.commit()
    return result
