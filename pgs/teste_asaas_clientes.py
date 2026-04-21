"""
Página de testes da API Asaas - Endpoint de Clientes.

Permite testar:
- Criar cliente no Asaas
- Listar clientes do Asaas
- Buscar cliente por ID
- Sincronizar cliente Asaas → Banco local
- Sincronizar cliente local → Asaas
- Sincronização em massa
"""

import asyncio
import json
from datetime import datetime

import streamlit as st

from database import create_session
from database.repositories import usuario_repo
from database.services.asaas_customer_service import (
    create_customer_in_asaas,
    get_asaas_client,
    get_asaas_customer,
    list_asaas_customers,
    register_cliente_with_asaas,
    sync_all_asaas_customers_to_local,
    sync_asaas_customer_to_local,
)
from api_asaas import AsaasError, CustomerCreateInput


def format_json(data: dict) -> str:
    """Formata dicionário como JSON indentado."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def show_result_card(title: str, success: bool, data: dict | str | None = None, error: str | None = None):
    """Exibe card com resultado de operação."""
    status_icon = "✅" if success else "❌"
    status_color = "green" if success else "red"
    
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 12px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba({'122,240,176' if success else '255,100,100'},0.3);
        margin-bottom: 1rem;
    ">
        <h4 style="color: {status_color}; margin: 0 0 0.5rem 0;">
            {status_icon} {title}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    if error:
        st.error(error)
    
    if data:
        if isinstance(data, dict):
            st.json(data)
        else:
            st.code(str(data))


def showTesteAsaasClientes():
    """Página principal de testes da API Asaas - Clientes."""
    
    st.title("🧪 Testes API Asaas - Clientes")
    st.markdown("Teste os endpoints de clientes da API Asaas no ambiente **sandbox**.")
    
    # Status da conexão
    with st.expander("🔌 Status da Conexão", expanded=False):
        if st.button("Verificar Conexão", key="btn_health"):
            try:
                async def check_health():
                    async with get_asaas_client() as client:
                        return await client.healthcheck()
                
                health = asyncio.run(check_health())
                show_result_card("Conexão OK", True, health)
            except Exception as e:
                show_result_card("Erro de Conexão", False, error=str(e))
    
    # Tabs de operações
    tab_criar, tab_listar, tab_buscar, tab_sync_local, tab_sync_asaas, tab_sync_massa = st.tabs([
        "➕ Criar Cliente",
        "📋 Listar Clientes",
        "🔍 Buscar por ID",
        "⬇️ Asaas → Local",
        "⬆️ Local → Asaas",
        "🔄 Sync em Massa",
    ])
    
    # ══════════════════════════════════════════════════════════════
    # TAB: CRIAR CLIENTE
    # ══════════════════════════════════════════════════════════════
    with tab_criar:
        st.subheader("➕ Criar Novo Cliente no Asaas")
        st.markdown("Cria cliente diretamente no Asaas (sandbox).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo *", key="criar_nome")
            email = st.text_input("E-mail", key="criar_email")
            cpf_cnpj = st.text_input("CPF/CNPJ", key="criar_cpf", help="Somente números")
            whatsapp = st.text_input("WhatsApp", key="criar_whatsapp")
        
        with col2:
            cep = st.text_input("CEP", key="criar_cep")
            endereco = st.text_input("Endereço", key="criar_endereco")
            numero = st.text_input("Número", key="criar_numero")
            bairro = st.text_input("Bairro", key="criar_bairro")
        
        observacoes = st.text_area("Observações", key="criar_obs")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            criar_apenas_asaas = st.button(
                "📤 Criar apenas no Asaas",
                use_container_width=True,
                key="btn_criar_asaas",
            )
        
        with col_btn2:
            criar_completo = st.button(
                "📦 Criar no Asaas + Banco Local",
                use_container_width=True,
                key="btn_criar_completo",
                type="primary",
            )
        
        if criar_apenas_asaas:
            if not nome:
                st.error("Nome é obrigatório.")
            else:
                with st.spinner("Criando cliente no Asaas..."):
                    try:
                        async def criar_no_asaas():
                            async with get_asaas_client() as client:
                                payload = CustomerCreateInput(
                                    name=nome,
                                    email=email or None,
                                    cpf_cnpj=cpf_cnpj or None,
                                    mobile_phone=whatsapp or None,
                                    postal_code=cep or None,
                                    address=endereco or None,
                                    address_number=numero or None,
                                    province=bairro or None,
                                    observations=observacoes or None,
                                )
                                return await client.create_customer(payload)
                        
                        result = asyncio.run(criar_no_asaas())
                        show_result_card("Cliente criado no Asaas", True, result)
                        
                    except AsaasError as e:
                        show_result_card("Erro ao criar cliente", False, error=str(e))
                    except Exception as e:
                        show_result_card("Erro inesperado", False, error=str(e))
        
        if criar_completo:
            if not nome or not email or not whatsapp:
                st.error("Nome, E-mail e WhatsApp são obrigatórios para criar no banco local.")
            else:
                with st.spinner("Criando cliente no Asaas + Banco Local..."):
                    try:
                        async def criar_completo_fn():
                            session = await create_session()
                            try:
                                return await register_cliente_with_asaas(
                                    session,
                                    nome=nome,
                                    email=email,
                                    whatsapp=whatsapp,
                                    password="temp123456",  # Senha temporária
                                    cpf_cnpj=cpf_cnpj or None,
                                    cep=cep or None,
                                    endereco=endereco or None,
                                    numero=numero or None,
                                    bairro=bairro or None,
                                )
                            finally:
                                await session.close()
                        
                        result = asyncio.run(criar_completo_fn())
                        
                        if result.success:
                            st.success(f"Cliente criado com sucesso!")
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                st.markdown("**Usuário Local:**")
                                if result.usuario:
                                    st.json({
                                        "id": result.usuario.id,
                                        "nome": result.usuario.nome,
                                        "email": result.usuario.email,
                                        "asaas_customer_id": result.usuario.asaas_customer_id,
                                    })
                            with col_r2:
                                st.markdown("**Cliente Asaas:**")
                                if result.asaas_customer:
                                    st.json(result.asaas_customer)
                        else:
                            show_result_card("Erro", False, error=result.error)
                        
                    except Exception as e:
                        show_result_card("Erro inesperado", False, error=str(e))
    
    # ══════════════════════════════════════════════════════════════
    # TAB: LISTAR CLIENTES
    # ══════════════════════════════════════════════════════════════
    with tab_listar:
        st.subheader("📋 Listar Clientes do Asaas")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_nome = st.text_input("Filtrar por nome", key="list_nome")
        with col_f2:
            filtro_email = st.text_input("Filtrar por e-mail", key="list_email")
        with col_f3:
            filtro_cpf = st.text_input("Filtrar por CPF/CNPJ", key="list_cpf")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            offset = st.number_input("Offset", min_value=0, value=0, key="list_offset")
        with col_p2:
            limit = st.number_input("Limit", min_value=1, max_value=100, value=20, key="list_limit")
        
        if st.button("🔍 Buscar Clientes", use_container_width=True, key="btn_listar"):
            with st.spinner("Buscando clientes no Asaas..."):
                try:
                    async def listar():
                        return await list_asaas_customers(
                            name=filtro_nome or None,
                            email=filtro_email or None,
                            cpf_cnpj=filtro_cpf or None,
                            offset=int(offset),
                            limit=int(limit),
                        )
                    
                    result = asyncio.run(listar())
                    customers = result.get("data", [])
                    total = result.get("totalCount", len(customers))
                    has_more = result.get("hasMore", False)
                    
                    st.info(f"Encontrados: **{total}** clientes | Página: {len(customers)} | Mais: {'Sim' if has_more else 'Não'}")
                    
                    if customers:
                        for i, customer in enumerate(customers):
                            with st.expander(f"👤 {customer.get('name', 'Sem nome')} ({customer.get('id', '')})", expanded=i==0):
                                col_c1, col_c2 = st.columns(2)
                                with col_c1:
                                    st.write(f"**ID:** `{customer.get('id')}`")
                                    st.write(f"**Nome:** {customer.get('name')}")
                                    st.write(f"**E-mail:** {customer.get('email') or '-'}")
                                    st.write(f"**CPF/CNPJ:** {customer.get('cpfCnpj') or '-'}")
                                with col_c2:
                                    st.write(f"**Telefone:** {customer.get('phone') or '-'}")
                                    st.write(f"**Celular:** {customer.get('mobilePhone') or '-'}")
                                    st.write(f"**Cidade:** {customer.get('city') or '-'}")
                                    st.write(f"**Deletado:** {'Sim' if customer.get('deleted') else 'Não'}")
                                
                                if st.button(f"📥 Sincronizar para Local", key=f"sync_{customer.get('id')}"):
                                    st.session_state[f"sync_customer_{i}"] = customer
                    else:
                        st.warning("Nenhum cliente encontrado.")
                        
                except AsaasError as e:
                    show_result_card("Erro ao listar", False, error=str(e))
                except Exception as e:
                    show_result_card("Erro inesperado", False, error=str(e))
    
    # ══════════════════════════════════════════════════════════════
    # TAB: BUSCAR POR ID
    # ══════════════════════════════════════════════════════════════
    with tab_buscar:
        st.subheader("🔍 Buscar Cliente por ID")
        
        customer_id = st.text_input("ID do Cliente Asaas", key="busca_id", 
                                     placeholder="cus_xxxxxxxxxxxxx")
        
        if st.button("🔍 Buscar", use_container_width=True, key="btn_buscar_id"):
            if not customer_id:
                st.error("Informe o ID do cliente.")
            else:
                with st.spinner("Buscando cliente..."):
                    try:
                        result = asyncio.run(get_asaas_customer(customer_id))
                        
                        if result:
                            show_result_card("Cliente encontrado", True, result)
                        else:
                            show_result_card("Cliente não encontrado", False)
                            
                    except Exception as e:
                        show_result_card("Erro na busca", False, error=str(e))
    
    # ══════════════════════════════════════════════════════════════
    # TAB: SYNC ASAAS → LOCAL
    # ══════════════════════════════════════════════════════════════
    with tab_sync_local:
        st.subheader("⬇️ Sincronizar Cliente: Asaas → Banco Local")
        st.markdown("Importa um cliente do Asaas para o banco de dados local.")
        
        sync_customer_id = st.text_input("ID do Cliente Asaas", key="sync_local_id",
                                          placeholder="cus_xxxxxxxxxxxxx")
        
        if st.button("⬇️ Importar para Local", use_container_width=True, key="btn_sync_local"):
            if not sync_customer_id:
                st.error("Informe o ID do cliente.")
            else:
                with st.spinner("Sincronizando..."):
                    try:
                        async def sync_to_local():
                            # Busca cliente no Asaas
                            customer = await get_asaas_customer(sync_customer_id)
                            if not customer:
                                return None, "Cliente não encontrado no Asaas"
                            
                            # Sincroniza para local
                            session = await create_session()
                            try:
                                result = await sync_asaas_customer_to_local(session, customer)
                                return result, None
                            finally:
                                await session.close()
                        
                        result, error = asyncio.run(sync_to_local())
                        
                        if error:
                            show_result_card("Erro", False, error=error)
                        elif result and result.success:
                            st.success("Cliente sincronizado com sucesso!")
                            if result.created_in_local:
                                st.info("Novo usuário criado no banco local.")
                            else:
                                st.info("Usuário existente atualizado.")
                            
                            if result.usuario:
                                st.json({
                                    "id": result.usuario.id,
                                    "nome": result.usuario.nome,
                                    "email": result.usuario.email,
                                    "whatsapp": result.usuario.whatsapp,
                                    "asaas_customer_id": result.usuario.asaas_customer_id,
                                })
                        else:
                            show_result_card("Erro na sincronização", False, 
                                           error=result.error if result else "Erro desconhecido")
                            
                    except Exception as e:
                        show_result_card("Erro inesperado", False, error=str(e))
    
    # ══════════════════════════════════════════════════════════════
    # TAB: SYNC LOCAL → ASAAS
    # ══════════════════════════════════════════════════════════════
    with tab_sync_asaas:
        st.subheader("⬆️ Sincronizar Cliente: Banco Local → Asaas")
        st.markdown("Envia um usuário local para o Asaas.")
        
        # Lista usuários locais sem asaas_id
        try:
            async def list_local_users():
                session = await create_session()
                try:
                    return await usuario_repo.list_clientes(session, com_asaas=False)
                finally:
                    await session.close()
            
            usuarios_sem_asaas = asyncio.run(list_local_users())
            
            if usuarios_sem_asaas:
                st.info(f"**{len(usuarios_sem_asaas)}** clientes locais sem vínculo com Asaas.")
                
                usuario_selecionado = st.selectbox(
                    "Selecione o usuário",
                    options=[(u.id, f"{u.nome} ({u.email})") for u in usuarios_sem_asaas],
                    format_func=lambda x: x[1],
                    key="sync_asaas_select",
                )
                
                if st.button("⬆️ Enviar para Asaas", use_container_width=True, key="btn_sync_asaas"):
                    with st.spinner("Enviando para Asaas..."):
                        try:
                            async def sync_to_asaas():
                                session = await create_session()
                                try:
                                    usuario = await usuario_repo.get_usuario_by_id(
                                        session, usuario_selecionado[0]
                                    )
                                    if not usuario:
                                        return None, "Usuário não encontrado"
                                    
                                    result = await create_customer_in_asaas(session, usuario)
                                    return result, None
                                finally:
                                    await session.close()
                            
                            result, error = asyncio.run(sync_to_asaas())
                            
                            if error:
                                show_result_card("Erro", False, error=error)
                            elif result and result.success:
                                st.success("Cliente enviado para Asaas!")
                                col_r1, col_r2 = st.columns(2)
                                with col_r1:
                                    if result.usuario:
                                        st.markdown("**Usuário Atualizado:**")
                                        st.json({
                                            "id": result.usuario.id,
                                            "nome": result.usuario.nome,
                                            "asaas_customer_id": result.usuario.asaas_customer_id,
                                        })
                                with col_r2:
                                    if result.asaas_customer:
                                        st.markdown("**Cliente Asaas:**")
                                        st.json(result.asaas_customer)
                            else:
                                show_result_card("Erro", False, 
                                               error=result.error if result else "Erro desconhecido")
                                
                        except Exception as e:
                            show_result_card("Erro inesperado", False, error=str(e))
            else:
                st.success("Todos os clientes locais já estão sincronizados com o Asaas!")
                
        except Exception as e:
            st.error(f"Erro ao carregar usuários: {e}")
    
    # ══════════════════════════════════════════════════════════════
    # TAB: SYNC EM MASSA
    # ══════════════════════════════════════════════════════════════
    with tab_sync_massa:
        st.subheader("🔄 Sincronização em Massa")
        st.markdown("Importa **todos** os clientes do Asaas para o banco local.")
        
        st.warning("⚠️ Esta operação pode demorar dependendo da quantidade de clientes.")
        
        if st.button("🚀 Iniciar Sincronização em Massa", use_container_width=True, key="btn_sync_massa"):
            with st.spinner("Sincronizando todos os clientes do Asaas..."):
                try:
                    async def sync_all():
                        session = await create_session()
                        try:
                            return await sync_all_asaas_customers_to_local(session)
                        finally:
                            await session.close()
                    
                    results = asyncio.run(sync_all())
                    
                    success_count = sum(1 for r in results if r.success)
                    error_count = sum(1 for r in results if not r.success)
                    created_count = sum(1 for r in results if r.success and r.created_in_local)
                    updated_count = sum(1 for r in results if r.success and not r.created_in_local)
                    
                    st.success(f"""
                    **Sincronização concluída!**
                    - Total processados: {len(results)}
                    - Sucesso: {success_count}
                    - Novos criados: {created_count}
                    - Atualizados: {updated_count}
                    - Erros: {error_count}
                    """)
                    
                    if error_count > 0:
                        with st.expander("❌ Ver erros"):
                            for r in results:
                                if not r.success:
                                    customer_name = r.asaas_customer.get("name", "?") if r.asaas_customer else "?"
                                    st.error(f"**{customer_name}:** {r.error}")
                    
                except Exception as e:
                    show_result_card("Erro na sincronização em massa", False, error=str(e))


# Para executar standalone
if __name__ == "__main__":
    showTesteAsaasClientes()
