"""
Serviço de integração de clientes entre Chef Delivery e Asaas.

Responsável por sincronizar clientes entre o banco local e a API Asaas,
mantendo o vínculo via asaas_customer_id.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from api_asaas import (
    AsaasClient,
    AsaasConfig,
    AsaasError,
    CustomerCreateInput,
)
from database.models.usuario import Usuario
from database.repositories import usuario_repo

load_dotenv()


@dataclass
class CustomerSyncResult:
    """Resultado da sincronização de cliente."""
    success: bool
    usuario: Usuario | None = None
    asaas_customer: dict[str, Any] | None = None
    error: str | None = None
    created_in_asaas: bool = False
    created_in_local: bool = False


def get_asaas_client() -> AsaasClient:
    """Retorna cliente Asaas configurado com variáveis de ambiente."""
    api_key = os.getenv("ASAAS_API_KEY", "")
    environment = os.getenv("ASAAS_ENVIRONMENT", "sandbox")
    
    if not api_key:
        raise ValueError("ASAAS_API_KEY não configurada no .env")
    
    config = AsaasConfig(
        api_key=api_key,
        environment=environment,  # type: ignore
    )
    return AsaasClient(config)


def usuario_to_customer_input(usuario: Usuario) -> CustomerCreateInput:
    """Converte Usuario do banco para CustomerCreateInput do Asaas."""
    return CustomerCreateInput(
        name=usuario.nome,
        email=usuario.email,
        cpf_cnpj=usuario.cpf_cnpj,
        mobile_phone=usuario.whatsapp,
        postal_code=usuario.cep,
        address=usuario.endereco,
        address_number=usuario.numero,
        complement=usuario.complemento,
        province=usuario.bairro,
        external_reference=str(usuario.id),
        observations=f"Cliente Chef Delivery - ID Local: {usuario.id}",
    )


def asaas_customer_to_usuario_data(customer: dict[str, Any]) -> dict[str, Any]:
    """Converte dados do cliente Asaas para campos do Usuario."""
    return {
        "nome": customer.get("name", ""),
        "email": customer.get("email"),
        "whatsapp": customer.get("mobilePhone") or customer.get("phone") or "",
        "cpf_cnpj": customer.get("cpfCnpj"),
        "cep": customer.get("postalCode"),
        "endereco": customer.get("address"),
        "numero": customer.get("addressNumber"),
        "complemento": customer.get("complement"),
        "bairro": customer.get("province"),
        "asaas_customer_id": customer.get("id"),
    }


async def create_customer_in_asaas(
    session: AsyncSession,
    usuario: Usuario,
) -> CustomerSyncResult:
    """
    Cria cliente no Asaas a partir de um usuário local.
    
    Atualiza o campo asaas_customer_id do usuário após criação.
    """
    if usuario.asaas_customer_id:
        return CustomerSyncResult(
            success=True,
            usuario=usuario,
            error="Usuário já possui asaas_customer_id",
        )
    
    try:
        async with get_asaas_client() as client:
            payload = usuario_to_customer_input(usuario)
            
            # Tenta criar ou buscar cliente existente
            asaas_customer = await client.create_or_get_customer(payload)
            
            # Atualiza usuário com ID do Asaas
            usuario = await usuario_repo.update_usuario(
                session,
                usuario.id,
                asaas_customer_id=asaas_customer.get("id"),
            )
            
            return CustomerSyncResult(
                success=True,
                usuario=usuario,
                asaas_customer=asaas_customer,
                created_in_asaas=True,
            )
            
    except AsaasError as e:
        return CustomerSyncResult(
            success=False,
            usuario=usuario,
            error=f"Erro Asaas: {e}",
        )
    except Exception as e:
        return CustomerSyncResult(
            success=False,
            usuario=usuario,
            error=f"Erro inesperado: {e}",
        )


async def sync_asaas_customer_to_local(
    session: AsyncSession,
    asaas_customer: dict[str, Any],
    senha_hash: str | None = None,
) -> CustomerSyncResult:
    """
    Sincroniza cliente do Asaas para o banco local.
    
    Se já existe (por email, cpf_cnpj ou asaas_id), atualiza.
    Se não existe, cria novo usuário.
    """
    asaas_id = asaas_customer.get("id")
    email = asaas_customer.get("email")
    cpf_cnpj = asaas_customer.get("cpfCnpj")
    
    # Tenta encontrar usuário existente
    usuario = None
    
    if asaas_id:
        usuario = await usuario_repo.get_usuario_by_asaas_id(session, asaas_id)
    
    if not usuario and email:
        usuario = await usuario_repo.get_usuario_by_email(session, email)
    
    if not usuario and cpf_cnpj:
        usuario = await usuario_repo.get_usuario_by_cpf_cnpj(session, cpf_cnpj)
    
    customer_data = asaas_customer_to_usuario_data(asaas_customer)
    
    if usuario:
        # Atualiza usuário existente
        usuario = await usuario_repo.update_usuario(
            session,
            usuario.id,
            asaas_customer_id=asaas_id,
            # Atualiza apenas campos vazios
            cpf_cnpj=usuario.cpf_cnpj or customer_data.get("cpf_cnpj"),
            cep=usuario.cep or customer_data.get("cep"),
            endereco=usuario.endereco or customer_data.get("endereco"),
            numero=usuario.numero or customer_data.get("numero"),
            complemento=usuario.complemento or customer_data.get("complemento"),
            bairro=usuario.bairro or customer_data.get("bairro"),
        )
        
        return CustomerSyncResult(
            success=True,
            usuario=usuario,
            asaas_customer=asaas_customer,
            created_in_local=False,
        )
    
    # Cria novo usuário
    if not senha_hash:
        # Gera senha temporária hasheada
        from database.services.auth_service import hash_password
        import secrets
        senha_hash = hash_password(secrets.token_urlsafe(12))
    
    whatsapp = customer_data.get("whatsapp") or ""
    if not whatsapp:
        # WhatsApp é obrigatório - usa placeholder
        whatsapp = f"asaas_{asaas_id}"
    
    try:
        usuario = await usuario_repo.create_usuario(
            session,
            nome=customer_data.get("nome") or "Cliente Asaas",
            email=email or f"{asaas_id}@asaas.temp",
            whatsapp=whatsapp,
            senha_hash=senha_hash,
            role="cliente",
            cpf_cnpj=customer_data.get("cpf_cnpj"),
            cep=customer_data.get("cep"),
            endereco=customer_data.get("endereco"),
            numero=customer_data.get("numero"),
            complemento=customer_data.get("complemento"),
            bairro=customer_data.get("bairro"),
        )
        
        # Atualiza com asaas_customer_id
        usuario = await usuario_repo.update_usuario(
            session,
            usuario.id,
            asaas_customer_id=asaas_id,
        )
        
        return CustomerSyncResult(
            success=True,
            usuario=usuario,
            asaas_customer=asaas_customer,
            created_in_local=True,
        )
        
    except Exception as e:
        return CustomerSyncResult(
            success=False,
            asaas_customer=asaas_customer,
            error=f"Erro ao criar usuário local: {e}",
        )


async def get_asaas_customer(
    asaas_customer_id: str,
) -> dict[str, Any] | None:
    """Busca cliente no Asaas pelo ID."""
    try:
        async with get_asaas_client() as client:
            return await client.get_customer(asaas_customer_id)
    except AsaasError:
        return None


async def list_asaas_customers(
    *,
    name: str | None = None,
    email: str | None = None,
    cpf_cnpj: str | None = None,
    offset: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    """Lista clientes do Asaas com filtros."""
    async with get_asaas_client() as client:
        return await client.list_customers(
            name=name,
            email=email,
            cpf_cnpj=cpf_cnpj,
            offset=offset,
            limit=limit,
        )


async def sync_all_asaas_customers_to_local(
    session: AsyncSession,
) -> list[CustomerSyncResult]:
    """
    Sincroniza todos os clientes do Asaas para o banco local.
    
    Útil para importação inicial ou reconciliação.
    """
    results = []
    offset = 0
    limit = 100
    
    async with get_asaas_client() as client:
        while True:
            response = await client.list_customers(offset=offset, limit=limit)
            customers = response.get("data", [])
            
            if not customers:
                break
            
            for customer in customers:
                result = await sync_asaas_customer_to_local(session, customer)
                results.append(result)
            
            if not response.get("hasMore", False):
                break
            
            offset += limit
    
    return results


async def register_cliente_with_asaas(
    session: AsyncSession,
    *,
    nome: str,
    email: str,
    whatsapp: str,
    password: str,
    cpf_cnpj: str | None = None,
    cep: str | None = None,
    endereco: str | None = None,
    numero: str | None = None,
    complemento: str | None = None,
    bairro: str | None = None,
    cidade: str | None = None,
    imagem_perfil: str | None = None,
) -> CustomerSyncResult:
    """
    Registra novo cliente no banco local E no Asaas simultaneamente.
    
    Fluxo:
    1. Verifica se usuário já existe (por email ou whatsapp)
    2. Se existe, atualiza dados e sincroniza com Asaas
    3. Se não existe, cria usuário no banco local
    4. Cria cliente no Asaas
    5. Vincula asaas_customer_id ao usuário
    6. Retorna resultado consolidado
    """
    from database.services.auth_service import hash_password
    
    # 1. Verifica se usuário já existe
    usuario = await usuario_repo.get_usuario_by_email(session, email)
    if not usuario:
        usuario = await usuario_repo.get_usuario_by_whatsapp(session, whatsapp)
    
    if usuario:
        # Usuário já existe - atualiza dados se necessário
        update_data = {}
        if cpf_cnpj and not usuario.cpf_cnpj:
            update_data["cpf_cnpj"] = cpf_cnpj
        if cep and not usuario.cep:
            update_data["cep"] = cep
        if endereco and not usuario.endereco:
            update_data["endereco"] = endereco
        if numero and not usuario.numero:
            update_data["numero"] = numero
        if bairro and not usuario.bairro:
            update_data["bairro"] = bairro
        if cidade and not usuario.cidade:
            update_data["cidade"] = cidade
        if imagem_perfil and not usuario.imagem_perfil:
            update_data["imagem_perfil"] = imagem_perfil
        
        if update_data:
            usuario = await usuario_repo.update_usuario(session, usuario.id, **update_data)
        
        # Sincroniza com Asaas se ainda não tiver asaas_customer_id
        if not usuario.asaas_customer_id:
            result = await create_customer_in_asaas(session, usuario)
            result.created_in_local = False
            return result
        else:
            return CustomerSyncResult(
                success=True,
                usuario=usuario,
                error="Usuário já existe e já está sincronizado com Asaas",
                created_in_local=False,
                created_in_asaas=False,
            )
    
    # 2. Cria usuário local (novo)
    try:
        senha_hash = hash_password(password)
        usuario = await usuario_repo.create_usuario(
            session,
            nome=nome,
            email=email,
            whatsapp=whatsapp,
            senha_hash=senha_hash,
            role="cliente",
            cpf_cnpj=cpf_cnpj,
            cep=cep,
            endereco=endereco,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            imagem_perfil=imagem_perfil,
        )
    except Exception as e:
        return CustomerSyncResult(
            success=False,
            error=f"Erro ao criar usuário local: {e}",
        )
    
    # 3. Cria no Asaas
    result = await create_customer_in_asaas(session, usuario)
    result.created_in_local = True
    
    return result
