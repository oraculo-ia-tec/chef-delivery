from datetime import date, timedelta

import streamlit as st

from api_asaas import AsaasError, CustomerCreateInput, PaymentCreateInput, build_asaas_client
from configuracao import ASAAS_API_KEY, ASAAS_ENVIRONMENT


def _init_state() -> None:
    if "asaas_test_api_key" not in st.session_state:
        st.session_state.asaas_test_api_key = ASAAS_API_KEY
    if "asaas_test_environment" not in st.session_state:
        st.session_state.asaas_test_environment = ASAAS_ENVIRONMENT
    if "asaas_test_timeout" not in st.session_state:
        st.session_state.asaas_test_timeout = 30.0
    if "asaas_test_last_result" not in st.session_state:
        st.session_state.asaas_test_last_result = None
    if "asaas_test_last_error" not in st.session_state:
        st.session_state.asaas_test_last_error = None
    if "asaas_test_last_action" not in st.session_state:
        st.session_state.asaas_test_last_action = ""
    if "asaas_test_last_request" not in st.session_state:
        st.session_state.asaas_test_last_request = None


def _mask_secret(value: str) -> str:
    if not value:
        return "Nao configurada"
    if len(value) <= 10:
        return "*" * len(value)
    return f"{value[:6]}...{value[-4:]}"


def _store_success(action: str, request_data: dict, response_data: dict) -> None:
    st.session_state.asaas_test_last_action = action
    st.session_state.asaas_test_last_request = request_data
    st.session_state.asaas_test_last_result = response_data
    st.session_state.asaas_test_last_error = None


def _store_error(action: str, request_data: dict, exc: Exception) -> None:
    error_payload = {
        "message": str(exc),
        "type": type(exc).__name__,
    }
    if isinstance(exc, AsaasError):
        error_payload.update(
            {
                "status_code": exc.status_code,
                "details": exc.details,
                "response_body": exc.response_body,
            }
        )
    st.session_state.asaas_test_last_action = action
    st.session_state.asaas_test_last_request = request_data
    st.session_state.asaas_test_last_result = None
    st.session_state.asaas_test_last_error = error_payload


def _render_last_result() -> None:
    st.divider()
    st.subheader("Ultima execucao")
    st.caption(f"Acao: {st.session_state.asaas_test_last_action or 'Nenhuma'}")

    if st.session_state.asaas_test_last_request:
        st.markdown("**Payload enviado**")
        st.json(st.session_state.asaas_test_last_request)

    if st.session_state.asaas_test_last_result:
        st.success("Requisicao executada com sucesso.")
        st.markdown("**Resposta da API**")
        st.json(st.session_state.asaas_test_last_result)

    if st.session_state.asaas_test_last_error:
        st.error("A requisicao retornou erro.")
        st.markdown("**Detalhes do erro**")
        st.json(st.session_state.asaas_test_last_error)


async def _build_client():
    api_key = st.session_state.asaas_test_api_key.strip()
    environment = st.session_state.asaas_test_environment
    timeout = float(st.session_state.asaas_test_timeout)
    if not api_key:
        raise ValueError("Informe uma chave de API do Asaas para executar os testes.")
    return await build_asaas_client(api_key, environment=environment, timeout=timeout)


async def showTesteApi() -> None:
    _init_state()

    st.title("Teste da API")
    st.write(
        "Use esta pagina para validar solicitacoes da API do Asaas, inspecionar respostas e identificar erros antes de ajustar a integracao."
    )

    info_col, status_col, timeout_col = st.columns(3)
    info_col.metric("Ambiente", st.session_state.asaas_test_environment)
    status_col.metric("Chave ativa", _mask_secret(st.session_state.asaas_test_api_key))
    timeout_col.metric("Timeout", f"{float(st.session_state.asaas_test_timeout):.0f}s")

    config_tab, customers_tab, payments_tab, pix_tab = st.tabs(
        ["Configuracao", "Clientes", "Pagamentos", "PIX"]
    )

    with config_tab:
        with st.form("asaas-config-form"):
            api_key_value = st.text_input(
                "Chave da API do Asaas",
                value=st.session_state.asaas_test_api_key,
                type="password",
                help="Se deixar a chave configurada no segredo, voce pode apenas validar a conexao aqui.",
            )
            environment_value = st.selectbox(
                "Ambiente",
                options=["sandbox", "production"],
                index=0 if st.session_state.asaas_test_environment == "sandbox" else 1,
            )
            timeout_value = st.number_input(
                "Timeout da requisicao (segundos)",
                min_value=5.0,
                max_value=120.0,
                value=float(st.session_state.asaas_test_timeout),
                step=5.0,
            )
            submitted = st.form_submit_button("Salvar configuracao e testar conexao")

        if submitted:
            st.session_state.asaas_test_api_key = api_key_value
            st.session_state.asaas_test_environment = environment_value
            st.session_state.asaas_test_timeout = timeout_value

            request_data = {
                "environment": environment_value,
                "timeout": timeout_value,
                "api_key_masked": _mask_secret(api_key_value),
            }
            try:
                client = await _build_client()
                async with client:
                    response_data = await client.healthcheck()
                _store_success("healthcheck", request_data, response_data)
            except Exception as exc:
                _store_error("healthcheck", request_data, exc)

        st.info("A aba de configuracao salva o ambiente ativo e executa um healthcheck local do cliente Asaas.")

    with customers_tab:
        create_col, query_col = st.columns(2)

        with create_col:
            with st.form("asaas-create-customer-form"):
                st.markdown("### Criar cliente")
                customer_name = st.text_input("Nome", value="Cliente Teste Chef Delivery")
                customer_email = st.text_input("Email", value="cliente.teste@chefdelivery.com")
                customer_cpf = st.text_input("CPF ou CNPJ", value="12345678909")
                customer_phone = st.text_input("Celular", value="31999999999")
                customer_reference = st.text_input("Referencia externa", value="teste-cliente-streamlit")
                customer_notes = st.text_area("Observacoes", value="Cliente criado pela pagina de teste da API.")
                create_customer_submitted = st.form_submit_button("Enviar criacao de cliente")

            if create_customer_submitted:
                payload = CustomerCreateInput(
                    name=customer_name,
                    email=customer_email or None,
                    cpf_cnpj=customer_cpf or None,
                    mobile_phone=customer_phone or None,
                    external_reference=customer_reference or None,
                    observations=customer_notes or None,
                )
                request_data = payload.to_payload()
                try:
                    client = await _build_client()
                    async with client:
                        response_data = await client.create_customer(payload)
                    _store_success("create_customer", request_data, response_data)
                except Exception as exc:
                    _store_error("create_customer", request_data, exc)

        with query_col:
            with st.form("asaas-customer-query-form"):
                st.markdown("### Consultar ou listar clientes")
                customer_id = st.text_input("ID do cliente")
                list_name = st.text_input("Filtro por nome")
                list_email = st.text_input("Filtro por email")
                list_external_reference = st.text_input("Filtro por referencia externa")
                list_limit = st.number_input("Limite", min_value=1, max_value=100, value=10, step=1)
                query_mode = st.radio("Operacao", options=["Consultar por ID", "Listar clientes"], horizontal=True)
                customer_query_submitted = st.form_submit_button("Executar consulta de clientes")

            if customer_query_submitted:
                request_data = {
                    "operation": query_mode,
                    "customer_id": customer_id,
                    "name": list_name,
                    "email": list_email,
                    "external_reference": list_external_reference,
                    "limit": int(list_limit),
                }
                try:
                    client = await _build_client()
                    async with client:
                        if query_mode == "Consultar por ID":
                            if not customer_id.strip():
                                raise ValueError("Informe o ID do cliente para consulta individual.")
                            response_data = await client.get_customer(customer_id.strip())
                        else:
                            response_data = await client.list_customers(
                                name=list_name or None,
                                email=list_email or None,
                                external_reference=list_external_reference or None,
                                limit=int(list_limit),
                            )
                    _store_success("customer_query", request_data, response_data)
                except Exception as exc:
                    _store_error("customer_query", request_data, exc)

    with payments_tab:
        create_payment_col, get_payment_col = st.columns(2)

        with create_payment_col:
            with st.form("asaas-create-payment-form"):
                st.markdown("### Criar pagamento")
                payment_customer_id = st.text_input("ID do cliente", help="Use um customer id retornado pelo Asaas.")
                payment_billing_type = st.selectbox("Tipo de cobranca", options=["PIX", "BOLETO", "CREDIT_CARD", "UNDEFINED"])
                payment_value = st.number_input("Valor", min_value=0.01, value=25.0, step=1.0)
                payment_due_date = st.date_input("Data de vencimento", value=date.today() + timedelta(days=1), format="DD/MM/YYYY")
                payment_description = st.text_input("Descricao", value="Teste manual de cobranca via Streamlit")
                payment_reference = st.text_input("Referencia externa", value="teste-pagamento-streamlit")
                create_payment_submitted = st.form_submit_button("Criar pagamento")

            if create_payment_submitted:
                payload = PaymentCreateInput(
                    customer=payment_customer_id.strip(),
                    billing_type=payment_billing_type,
                    value=payment_value,
                    due_date=payment_due_date.isoformat(),
                    description=payment_description or None,
                    external_reference=payment_reference or None,
                )
                request_data = payload.to_payload()
                try:
                    if not payment_customer_id.strip():
                        raise ValueError("Informe o ID do cliente para criar o pagamento.")
                    client = await _build_client()
                    async with client:
                        response_data = await client.create_payment(payload)
                    _store_success("create_payment", request_data, response_data)
                except Exception as exc:
                    _store_error("create_payment", request_data, exc)

        with get_payment_col:
            with st.form("asaas-payment-query-form"):
                st.markdown("### Consultar ou listar pagamentos")
                payment_id = st.text_input("ID do pagamento")
                payment_customer_filter = st.text_input("Filtro por cliente")
                payment_status_filter = st.text_input("Filtro por status")
                payment_reference_filter = st.text_input("Filtro por referencia externa")
                payment_limit = st.number_input("Limite de pagamentos", min_value=1, max_value=100, value=10, step=1)
                payment_mode = st.radio("Operacao de pagamento", options=["Consultar por ID", "Listar pagamentos"], horizontal=True)
                payment_query_submitted = st.form_submit_button("Executar consulta de pagamentos")

            if payment_query_submitted:
                request_data = {
                    "operation": payment_mode,
                    "payment_id": payment_id,
                    "customer": payment_customer_filter,
                    "status": payment_status_filter,
                    "external_reference": payment_reference_filter,
                    "limit": int(payment_limit),
                }
                try:
                    client = await _build_client()
                    async with client:
                        if payment_mode == "Consultar por ID":
                            if not payment_id.strip():
                                raise ValueError("Informe o ID do pagamento para consulta individual.")
                            response_data = await client.get_payment(payment_id.strip())
                        else:
                            response_data = await client.list_payments(
                                customer=payment_customer_filter or None,
                                status=payment_status_filter or None,
                                external_reference=payment_reference_filter or None,
                                limit=int(payment_limit),
                            )
                    _store_success("payment_query", request_data, response_data)
                except Exception as exc:
                    _store_error("payment_query", request_data, exc)

    with pix_tab:
        with st.form("asaas-pix-qrcode-form"):
            st.markdown("### Consultar QR Code PIX")
            pix_payment_id = st.text_input("ID do pagamento PIX")
            pix_qrcode_submitted = st.form_submit_button("Consultar QR Code PIX")

        if pix_qrcode_submitted:
            request_data = {"payment_id": pix_payment_id}
            try:
                if not pix_payment_id.strip():
                    raise ValueError("Informe o ID do pagamento para consultar o QR Code PIX.")
                client = await _build_client()
                async with client:
                    qr_code = await client.get_pix_qr_code(pix_payment_id.strip())
                response_data = {
                    "encoded_image": qr_code.encoded_image,
                    "payload": qr_code.payload,
                    "expiration_date": qr_code.expiration_date,
                }
                _store_success("get_pix_qr_code", request_data, response_data)
                if qr_code.encoded_image:
                    st.image(f"data:image/png;base64,{qr_code.encoded_image}", caption="QR Code PIX retornado pelo Asaas")
            except Exception as exc:
                _store_error("get_pix_qr_code", request_data, exc)

    _render_last_result()