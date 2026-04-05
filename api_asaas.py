from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Literal

import httpx


AsaasEnvironment = Literal["sandbox", "production"]
AsaasBillingType = Literal["BOLETO", "CREDIT_CARD", "PIX", "UNDEFINED"]
PaymentMethod = Literal["pix", "credit_card_checkout", "credit_card_direct"]


class AsaasError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        details: list[dict[str, Any]] | None = None,
        response_body: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details or []
        self.response_body = response_body


@dataclass(slots=True)
class AsaasConfig:
    api_key: str
    environment: AsaasEnvironment = "sandbox"
    user_agent: str = "ChefDelivery/1.0"
    timeout: float = 30.0
    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        urls = {
            "sandbox": "https://api-sandbox.asaas.com/v3",
            "production": "https://api.asaas.com/v3",
        }
        self.base_url = urls[self.environment]


@dataclass(slots=True)
class CustomerCreateInput:
    name: str
    cpf_cnpj: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    postal_code: str | None = None
    address: str | None = None
    address_number: str | None = None
    complement: str | None = None
    province: str | None = None
    external_reference: str | None = None
    notification_disabled: bool | None = None
    additional_emails: str | None = None
    municipal_inscription: str | None = None
    state_inscription: str | None = None
    observations: str | None = None
    group_name: str | None = None
    company: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "cpfCnpj": self.cpf_cnpj,
            "email": self.email,
            "phone": self.phone,
            "mobilePhone": self.mobile_phone,
            "postalCode": self.postal_code,
            "address": self.address,
            "addressNumber": self.address_number,
            "complement": self.complement,
            "province": self.province,
            "externalReference": self.external_reference,
            "notificationDisabled": self.notification_disabled,
            "additionalEmails": self.additional_emails,
            "municipalInscription": self.municipal_inscription,
            "stateInscription": self.state_inscription,
            "observations": self.observations,
            "groupName": self.group_name,
            "company": self.company,
        }
        return {k: v for k, v in payload.items() if v is not None}


@dataclass(slots=True)
class CreditCardInfo:
    holder_name: str
    number: str
    expiry_month: str
    expiry_year: str
    ccv: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "holderName": self.holder_name,
            "number": self.number,
            "expiryMonth": self.expiry_month,
            "expiryYear": self.expiry_year,
            "ccv": self.ccv,
        }


@dataclass(slots=True)
class CreditCardHolderInfo:
    name: str
    email: str
    cpf_cnpj: str
    postal_code: str
    address_number: str
    phone: str | None = None
    mobile_phone: str | None = None
    address_complement: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "name": self.name,
            "email": self.email,
            "cpfCnpj": self.cpf_cnpj,
            "postalCode": self.postal_code,
            "addressNumber": self.address_number,
            "phone": self.phone,
            "mobilePhone": self.mobile_phone,
            "addressComplement": self.address_complement,
        }
        return {k: v for k, v in payload.items() if v is not None}


@dataclass(slots=True)
class PaymentCreateInput:
    customer: str
    billing_type: AsaasBillingType
    value: Decimal | float | str
    due_date: str
    description: str | None = None
    external_reference: str | None = None
    postal_service: bool | None = None
    installment_count: int | None = None
    installment_value: Decimal | float | str | None = None
    total_value: Decimal | float | str | None = None
    remote_ip: str | None = None
    credit_card: CreditCardInfo | None = None
    credit_card_holder_info: CreditCardHolderInfo | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "customer": self.customer,
            "billingType": self.billing_type,
            "value": float(Decimal(str(self.value))),
            "dueDate": self.due_date,
            "description": self.description,
            "externalReference": self.external_reference,
            "postalService": self.postal_service,
            "installmentCount": self.installment_count,
            "installmentValue": float(Decimal(str(self.installment_value))) if self.installment_value is not None else None,
            "totalValue": float(Decimal(str(self.total_value))) if self.total_value is not None else None,
            "remoteIp": self.remote_ip,
            "creditCard": self.credit_card.to_payload() if self.credit_card else None,
            "creditCardHolderInfo": self.credit_card_holder_info.to_payload() if self.credit_card_holder_info else None,
        }
        return {k: v for k, v in payload.items() if v is not None}


@dataclass(slots=True)
class ChefCustomerData:
    name: str
    email: str | None = None
    cpf_cnpj: str | None = None
    phone: str | None = None
    mobile_phone: str | None = None
    postal_code: str | None = None
    address: str | None = None
    address_number: str | None = None
    complement: str | None = None
    province: str | None = None
    external_reference: str | None = None
    observations: str | None = None


@dataclass(slots=True)
class ChefOrderData:
    order_id: str
    customer: ChefCustomerData
    total_value: Decimal | float | str
    due_date: str
    description: str
    payment_method: PaymentMethod = "pix"
    remote_ip: str | None = None
    credit_card: CreditCardInfo | None = None
    credit_card_holder_info: CreditCardHolderInfo | None = None

    @property
    def external_reference(self) -> str:
        return self.order_id


@dataclass(slots=True)
class PixQrCodeResponse:
    encoded_image: str | None
    payload: str | None
    expiration_date: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "PixQrCodeResponse":
        return cls(
            encoded_image=data.get("encodedImage"),
            payload=data.get("payload"),
            expiration_date=data.get("expirationDate"),
        )


@dataclass(slots=True)
class CheckoutPaymentResponse:
    payment_id: str | None
    status: str | None
    value: Any | None
    net_value: Any | None
    billing_type: str | None
    invoice_url: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "CheckoutPaymentResponse":
        return cls(
            payment_id=data.get("id"),
            status=data.get("status"),
            value=data.get("value"),
            net_value=data.get("netValue"),
            billing_type=data.get("billingType"),
            invoice_url=data.get("invoiceUrl"),
        )


@dataclass(slots=True)
class ChefPaymentResult:
    order_id: str
    payment_method: PaymentMethod
    customer_id: str | None
    payment_id: str | None
    status: str | None
    value: Any | None
    invoice_url: str | None = None
    pix_payload: str | None = None
    pix_qr_code_base64: str | None = None
    pix_expiration_date: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AsaasClient:
    def __init__(self, config: AsaasConfig) -> None:
        self.config = config
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": self.config.user_agent,
            "access_token": self.config.api_key,
        }

    async def __aenter__(self) -> "AsaasClient":
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self.headers,
            timeout=self.config.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=self.headers,
                timeout=self.config.timeout,
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        client = await self._ensure_client()
        response = await client.request(method, path, params=params, json=json, timeout=timeout)
        content_type = response.headers.get("content-type", "")

        try:
            data = response.json() if "application/json" in content_type else {"raw": response.text}
        except ValueError:
            data = {"raw": response.text}

        if response.is_error:
            details = data.get("errors") if isinstance(data, dict) else None
            message = self._extract_error_message(data) or f"Erro HTTP {response.status_code} ao acessar Asaas"
            raise AsaasError(
                message,
                status_code=response.status_code,
                details=details,
                response_body=data,
            )

        if isinstance(data, dict):
            return data
        return {"data": data}

    @staticmethod
    def _extract_error_message(data: Any) -> str | None:
        if not isinstance(data, dict):
            return None
        errors = data.get("errors")
        if isinstance(errors, list) and errors:
            first = errors[0]
            if isinstance(first, dict):
                code = first.get("code")
                description = first.get("description")
                if code and description:
                    return f"{code}: {description}"
                if description:
                    return str(description)
        return data.get("message")

    async def healthcheck(self) -> dict[str, Any]:
        return {
            "base_url": self.config.base_url,
            "environment": self.config.environment,
            "user_agent": self.config.user_agent,
        }

    async def create_customer(self, payload: CustomerCreateInput) -> dict[str, Any]:
        return await self._request("POST", "/customers", json=payload.to_payload())

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/customers/{customer_id}")

    async def list_customers(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        cpf_cnpj: str | None = None,
        external_reference: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        params = {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj,
            "externalReference": external_reference,
            "offset": offset,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", "/customers", params=params)

    async def find_customer_by_external_reference(self, external_reference: str) -> dict[str, Any] | None:
        data = await self.list_customers(external_reference=external_reference, limit=1)
        items = data.get("data") or []
        return items[0] if items else None

    async def create_or_get_customer(self, payload: CustomerCreateInput) -> dict[str, Any]:
        if payload.external_reference:
            existing = await self.find_customer_by_external_reference(payload.external_reference)
            if existing:
                return existing
        return await self.create_customer(payload)

    async def create_payment(self, payload: PaymentCreateInput, *, timeout: float | None = None) -> dict[str, Any]:
        return await self._request("POST", "/payments", json=payload.to_payload(), timeout=timeout)

    async def get_payment(self, payment_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/payments/{payment_id}")

    async def list_payments(
        self,
        *,
        customer: str | None = None,
        billing_type: AsaasBillingType | None = None,
        status: str | None = None,
        external_reference: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        params = {
            "customer": customer,
            "billingType": billing_type,
            "status": status,
            "externalReference": external_reference,
            "offset": offset,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", "/payments", params=params)

    async def get_pix_qr_code(self, payment_id: str) -> PixQrCodeResponse:
        data = await self._request("GET", f"/payments/{payment_id}/pixQrCode")
        return PixQrCodeResponse.from_api(data)

    async def create_pix_payment(self, payload: PaymentCreateInput) -> dict[str, Any]:
        if payload.billing_type != "PIX":
            raise ValueError("create_pix_payment exige billing_type='PIX'")
        return await self.create_payment(payload)

    async def create_credit_card_payment_redirect(self, payload: PaymentCreateInput) -> CheckoutPaymentResponse:
        if payload.billing_type != "CREDIT_CARD":
            raise ValueError("create_credit_card_payment_redirect exige billing_type='CREDIT_CARD'")
        data = await self.create_payment(payload)
        return CheckoutPaymentResponse.from_api(data)

    async def create_credit_card_payment_direct(self, payload: PaymentCreateInput) -> CheckoutPaymentResponse:
        if payload.billing_type != "CREDIT_CARD":
            raise ValueError("create_credit_card_payment_direct exige billing_type='CREDIT_CARD'")
        if not payload.credit_card or not payload.credit_card_holder_info or not payload.remote_ip:
            raise ValueError("Pagamento direto em cartão exige credit_card, credit_card_holder_info e remote_ip")
        data = await self.create_payment(payload, timeout=max(self.config.timeout, 60.0))
        return CheckoutPaymentResponse.from_api(data)

    async def create_order_pix_charge(
        self,
        *,
        customer_id: str,
        value: Decimal | float | str,
        due_date: str,
        description: str,
        external_reference: str | None = None,
    ) -> dict[str, Any]:
        payment = await self.create_pix_payment(
            PaymentCreateInput(
                customer=customer_id,
                billing_type="PIX",
                value=value,
                due_date=due_date,
                description=description,
                external_reference=external_reference,
            )
        )
        qr_code = await self.get_pix_qr_code(payment["id"])
        return {
            "payment": payment,
            "pix_qr_code": {
                "encoded_image": qr_code.encoded_image,
                "payload": qr_code.payload,
                "expiration_date": qr_code.expiration_date,
            },
        }

    async def create_order_card_checkout(
        self,
        *,
        customer_id: str,
        value: Decimal | float | str,
        due_date: str,
        description: str,
        external_reference: str | None = None,
    ) -> dict[str, Any]:
        result = await self.create_credit_card_payment_redirect(
            PaymentCreateInput(
                customer=customer_id,
                billing_type="CREDIT_CARD",
                value=value,
                due_date=due_date,
                description=description,
                external_reference=external_reference,
            )
        )
        return {
            "payment_id": result.payment_id,
            "status": result.status,
            "billing_type": result.billing_type,
            "invoice_url": result.invoice_url,
            "value": result.value,
            "net_value": result.net_value,
        }


class ChefDeliveryAsaasService:
    def __init__(self, client: AsaasClient) -> None:
        self.client = client

    @staticmethod
    def build_customer_input(customer: ChefCustomerData) -> CustomerCreateInput:
        return CustomerCreateInput(
            name=customer.name,
            email=customer.email,
            cpf_cnpj=customer.cpf_cnpj,
            phone=customer.phone,
            mobile_phone=customer.mobile_phone,
            postal_code=customer.postal_code,
            address=customer.address,
            address_number=customer.address_number,
            complement=customer.complement,
            province=customer.province,
            external_reference=customer.external_reference,
            observations=customer.observations,
        )

    async def ensure_customer(self, customer: ChefCustomerData) -> dict[str, Any]:
        payload = self.build_customer_input(customer)
        return await self.client.create_or_get_customer(payload)

    async def create_order_payment(self, order: ChefOrderData) -> ChefPaymentResult:
        customer = await self.ensure_customer(order.customer)
        customer_id = customer.get("id")

        if order.payment_method == "pix":
            result = await self.client.create_order_pix_charge(
                customer_id=customer_id,
                value=order.total_value,
                due_date=order.due_date,
                description=order.description,
                external_reference=order.external_reference,
            )
            payment = result["payment"]
            pix = result["pix_qr_code"]
            return ChefPaymentResult(
                order_id=order.order_id,
                payment_method=order.payment_method,
                customer_id=customer_id,
                payment_id=payment.get("id"),
                status=payment.get("status"),
                value=payment.get("value"),
                pix_payload=pix.get("payload"),
                pix_qr_code_base64=pix.get("encoded_image"),
                pix_expiration_date=pix.get("expiration_date"),
                raw=result,
            )

        if order.payment_method == "credit_card_checkout":
            result = await self.client.create_order_card_checkout(
                customer_id=customer_id,
                value=order.total_value,
                due_date=order.due_date,
                description=order.description,
                external_reference=order.external_reference,
            )
            return ChefPaymentResult(
                order_id=order.order_id,
                payment_method=order.payment_method,
                customer_id=customer_id,
                payment_id=result.get("payment_id"),
                status=result.get("status"),
                value=result.get("value"),
                invoice_url=result.get("invoice_url"),
                raw=result,
            )

        if order.payment_method == "credit_card_direct":
            payload = PaymentCreateInput(
                customer=customer_id,
                billing_type="CREDIT_CARD",
                value=order.total_value,
                due_date=order.due_date,
                description=order.description,
                external_reference=order.external_reference,
                remote_ip=order.remote_ip,
                credit_card=order.credit_card,
                credit_card_holder_info=order.credit_card_holder_info,
            )
            result = await self.client.create_credit_card_payment_direct(payload)
            return ChefPaymentResult(
                order_id=order.order_id,
                payment_method=order.payment_method,
                customer_id=customer_id,
                payment_id=result.payment_id,
                status=result.status,
                value=result.value,
                invoice_url=result.invoice_url,
                raw=asdict(result),
            )

        raise ValueError(f"Método de pagamento não suportado: {order.payment_method}")

    async def get_order_payment_status(self, payment_id: str) -> dict[str, Any]:
        payment = await self.client.get_payment(payment_id)
        return {
            "payment_id": payment.get("id"),
            "status": payment.get("status"),
            "billing_type": payment.get("billingType"),
            "value": payment.get("value"),
            "net_value": payment.get("netValue"),
            "invoice_url": payment.get("invoiceUrl"),
            "confirmed_date": payment.get("confirmedDate"),
            "payment_date": payment.get("paymentDate"),
            "external_reference": payment.get("externalReference"),
            "description": payment.get("description"),
            "raw": payment,
        }

    @staticmethod
    def parse_webhook_event(payload: dict[str, Any]) -> dict[str, Any]:
        payment = payload.get("payment") or {}
        return {
            "event_id": payload.get("id"),
            "event": payload.get("event"),
            "date_created": payload.get("dateCreated"),
            "payment_id": payment.get("id"),
            "status": payment.get("status"),
            "billing_type": payment.get("billingType"),
            "external_reference": payment.get("externalReference"),
            "description": payment.get("description"),
            "value": payment.get("value"),
            "net_value": payment.get("netValue"),
            "invoice_url": payment.get("invoiceUrl"),
            "raw": payload,
        }

    @staticmethod
    def should_mark_order_paid(event_name: str) -> bool:
        return event_name in {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED", "CHECKOUT_PAID"}

    @staticmethod
    def should_mark_order_failed(event_name: str) -> bool:
        return event_name in {
            "PAYMENT_REPROVED_BY_RISK_ANALYSIS",
            "PAYMENT_CREDIT_CARD_CAPTURE_REFUSED",
            "PAYMENT_DELETED",
            "PAYMENT_REFUNDED",
            "PAYMENT_CHARGEBACK_REQUESTED",
            "CHECKOUT_CANCELED",
            "CHECKOUT_EXPIRED",
        }


def build_order_from_session_state(session_state: Any, *, due_date: str, order_id: str, total_value: Decimal | float | str, payment_method: PaymentMethod = "pix", email: str | None = None, cpf_cnpj: str | None = None, postal_code: str | None = None, address_number: str | None = None, province: str | None = None, remote_ip: str | None = None) -> ChefOrderData:
    customer = ChefCustomerData(
        name=session_state.get("name") or session_state.get("primeiro_nome") or "Cliente Chef Delivery",
        email=email,
        cpf_cnpj=cpf_cnpj,
        phone=session_state.get("whatsapp"),
        mobile_phone=session_state.get("whatsapp"),
        postal_code=postal_code,
        address=session_state.get("endereco"),
        address_number=address_number,
        province=province,
        external_reference=str(session_state.get("username") or order_id),
        observations=session_state.get("observacao"),
    )
    description = session_state.get("pedido_texto") or session_state.get("pedido") or "Pedido Chef Delivery"
    if isinstance(description, list):
        description = ", ".join(map(str, description))
    return ChefOrderData(
        order_id=order_id,
        customer=customer,
        total_value=total_value,
        due_date=due_date,
        description=str(description),
        payment_method=payment_method,
        remote_ip=remote_ip,
    )


async def create_payment_from_streamlit_session(service: ChefDeliveryAsaasService, session_state: Any, *, due_date: str, order_id: str, total_value: Decimal | float | str, payment_method: PaymentMethod = "pix", email: str | None = None, cpf_cnpj: str | None = None, postal_code: str | None = None, address_number: str | None = None, province: str | None = None, remote_ip: str | None = None) -> dict[str, Any]:
    order = build_order_from_session_state(
        session_state,
        due_date=due_date,
        order_id=order_id,
        total_value=total_value,
        payment_method=payment_method,
        email=email,
        cpf_cnpj=cpf_cnpj,
        postal_code=postal_code,
        address_number=address_number,
        province=province,
        remote_ip=remote_ip,
    )
    result = await service.create_order_payment(order)
    return result.to_dict()


async def streamlit_payment_flow_example(session_state: Any, *, api_key: str, environment: AsaasEnvironment, due_date: str, order_id: str, total_value: Decimal | float | str, payment_method: PaymentMethod = "pix", email: str | None = None, cpf_cnpj: str | None = None, postal_code: str | None = None, address_number: str | None = None, province: str | None = None, remote_ip: str | None = None) -> dict[str, Any]:
    client = await build_asaas_client(api_key, environment=environment)
    async with client:
        service = ChefDeliveryAsaasService(client)
        return await create_payment_from_streamlit_session(
            service,
            session_state,
            due_date=due_date,
            order_id=order_id,
            total_value=total_value,
            payment_method=payment_method,
            email=email,
            cpf_cnpj=cpf_cnpj,
            postal_code=postal_code,
            address_number=address_number,
            province=province,
            remote_ip=remote_ip,
        )


def handle_asaas_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    parsed = ChefDeliveryAsaasService.parse_webhook_event(payload)
    event_name = parsed.get("event") or ""
    parsed["mark_as_paid"] = ChefDeliveryAsaasService.should_mark_order_paid(event_name)
    parsed["mark_as_failed"] = ChefDeliveryAsaasService.should_mark_order_failed(event_name)
    return parsed


MCP_EXPOSED_TOOLS = {
    "create_order_payment": {
        "description": "Cria cobrança Asaas para um pedido do Chef Delivery via Pix, checkout de cartão ou cartão direto.",
        "input_model": "ChefOrderData",
    },
    "get_order_payment_status": {
        "description": "Consulta o status atualizado de uma cobrança Asaas pelo payment_id.",
        "input_model": "payment_id:str",
    },
    "handle_asaas_webhook_payload": {
        "description": "Interpreta o payload recebido no webhook do Asaas e indica ação de negócio para o pedido.",
        "input_model": "dict",
    },
}


async def build_asaas_client(
    api_key: str,
    *,
    environment: AsaasEnvironment = "sandbox",
    user_agent: str = "ChefDelivery/1.0",
    timeout: float = 30.0,
) -> AsaasClient:
    config = AsaasConfig(
        api_key=api_key,
        environment=environment,
        user_agent=user_agent,
        timeout=timeout,
    )
    return AsaasClient(config)
