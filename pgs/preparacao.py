import streamlit as st
import pandas as pd
from datetime import datetime


def _init_preparacao_state():
    """Inicializa filas de preparação no session_state."""
    if "fila_preparando" not in st.session_state:
        # Pedidos que chegaram com pagamento confirmado (webhook ASAAS)
        st.session_state.fila_preparando = [
            {
                "pedido_id": "PROD-A1B2C3D4",
                "cliente": "Ramone Teste",
                "whatsapp": "(31) 99999-0001",
                "endereco": "Rua das Flores, 123 - Bairro Centro",
                "itens": "Picanha suína 3kg, Linguiça caseira 2kg",
                "valor": 130.95,
                "horario_chegada": "2026-04-05 10:15:00",
                "inicio_preparacao": None,
                "fim_preparacao": None,
                "status": "aguardando",
            },
            {
                "pedido_id": "PROD-E5F6G7H8",
                "cliente": "Adriano Stellantis",
                "whatsapp": "(31) 99999-0002",
                "endereco": "Av. Brasil, 456 - Bairro Savassi",
                "itens": "Kit Gold, Coca-Cola 2L",
                "valor": 159.98,
                "horario_chegada": "2026-04-05 10:22:00",
                "inicio_preparacao": None,
                "fim_preparacao": None,
                "status": "aguardando",
            },
            {
                "pedido_id": "PROD-I9J0K1L2",
                "cliente": "Vovô Tec",
                "whatsapp": "(31) 99999-0003",
                "endereco": "Rua Minas Gerais, 789 - Bairro Funcionários",
                "itens": "Contra filé 5kg, Fraldinha 2kg, Carvão 3kg",
                "valor": 265.92,
                "horario_chegada": "2026-04-05 10:30:00",
                "inicio_preparacao": "2026-04-05 10:35:00",
                "fim_preparacao": None,
                "status": "preparando",
            },
        ]

    if "fila_entrega" not in st.session_state:
        st.session_state.fila_entrega = []

    if "historico_entregas" not in st.session_state:
        st.session_state.historico_entregas = []

    # Garante que entregadores existam
    if "entregadores" not in st.session_state:
        st.session_state.entregadores = []


def _formatar_dt(dt_str: str | None) -> str:
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return str(dt_str)


def _formatar_hora(dt_str: str | None) -> str:
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return str(dt_str)


# ═══════════════════════════════════════════
# CSS GLOBAL DA PÁGINA
# ═══════════════════════════════════════════
_CSS = """
<style>
/* ── Card de pedido em preparação ── */
.prep-card {
    position: relative;
    padding: 1.2rem 1.4rem;
    border-radius: 18px;
    margin-bottom: 1rem;
    background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(120,255,182,0.14);
    box-shadow: 0 0 20px rgba(0,255,170,0.04);
    animation: slideInPrep 0.5s ease-out;
}
.prep-card-aguardando { border-left: 4px solid #ffd700; }
.prep-card-preparando { border-left: 4px solid #7af0b0; }
.prep-card-pronto     { border-left: 4px solid #5ec8ff; }

.prep-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}
.prep-header .pedido-id {
    font-weight: 700;
    font-size: 1rem;
    color: #fff;
}

/* ── Barra de progresso animada ── */
.progress-bar-wrap {
    height: 6px;
    border-radius: 99px;
    background: rgba(255,255,255,0.08);
    margin: 0.8rem 0;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}
.progress-fill-aguardando {
    width: 15%;
    background: linear-gradient(90deg, #ffd700, #ffec80);
    animation: pulseBar 1.8s ease-in-out infinite;
}
.progress-fill-preparando {
    width: 60%;
    background: linear-gradient(90deg, #7af0b0, #5ec8ff);
    animation: pulseBar 1.4s ease-in-out infinite;
}
.progress-fill-pronto {
    width: 100%;
    background: linear-gradient(90deg, #5ec8ff, #a78bfa);
}

/* ── Status badges ── */
.badge-aguardando {
    display: inline-block; padding: 0.22rem 0.55rem; border-radius: 999px;
    background: rgba(255,215,0,0.15); border: 1px solid rgba(255,215,0,0.3);
    color: #ffd700; font-size: 0.78rem; font-weight: 600;
    animation: pulseBadge 2s ease-in-out infinite;
}
.badge-preparando {
    display: inline-block; padding: 0.22rem 0.55rem; border-radius: 999px;
    background: rgba(122,240,176,0.15); border: 1px solid rgba(122,240,176,0.3);
    color: #7af0b0; font-size: 0.78rem; font-weight: 600;
    animation: pulseBadge 1.6s ease-in-out infinite;
}
.badge-pronto {
    display: inline-block; padding: 0.22rem 0.55rem; border-radius: 999px;
    background: rgba(94,200,255,0.15); border: 1px solid rgba(94,200,255,0.3);
    color: #5ec8ff; font-size: 0.78rem; font-weight: 600;
}

/* ── Timeline ── */
.timeline {
    display: flex;
    gap: 1.4rem;
    margin: 0.6rem 0;
    font-size: 0.85rem;
    color: #c0d8e8;
}
.timeline-item {
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.timeline-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-gold { background: #ffd700; box-shadow: 0 0 8px rgba(255,215,0,0.5); }
.dot-green { background: #7af0b0; box-shadow: 0 0 8px rgba(122,240,176,0.5); }
.dot-blue { background: #5ec8ff; box-shadow: 0 0 8px rgba(94,200,255,0.5); }
.dot-gray { background: #555; }

/* ── Entrega card ── */
.entrega-card {
    padding: 1rem 1.2rem;
    border-radius: 16px;
    background: linear-gradient(145deg, rgba(94,200,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(94,200,255,0.18);
    margin-bottom: 0.6rem;
    animation: slideInPrep 0.4s ease-out;
}

@keyframes slideInPrep {
    from { opacity: 0; transform: translateX(-16px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulseBar {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.55; }
}
@keyframes pulseBadge {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.7; transform: scale(1.05); }
}
</style>
"""


def _render_tab_preparando():
    """Tab 1 — Pedidos pagos aguardando / em preparação."""
    fila = st.session_state.fila_preparando

    if not fila:
        st.info("Nenhum pedido na fila de preparação no momento.")
        return

    # Ordena por horário de chegada
    fila_sorted = sorted(fila, key=lambda p: p["horario_chegada"])

    for idx, pedido in enumerate(fila_sorted):
        status = pedido["status"]
        css_class = f"prep-card prep-card-{status}"
        badge_class = f"badge-{status}"
        progress_class = f"progress-fill progress-fill-{status}"

        status_labels = {
            "aguardando": "⏳ Aguardando preparo",
            "preparando": "🔥 Em preparação",
            "pronto": "✅ Pronto",
        }

        # ── Card HTML ──
        st.markdown(f"""
        <div class="{css_class}">
            <div class="prep-header">
                <span class="pedido-id">🧾 {pedido['pedido_id']}</span>
                <span class="{badge_class}">{status_labels.get(status, status)}</span>
            </div>
            <div style="color:#e0ecf5; font-size:0.92rem;">
                <strong>{pedido['cliente']}</strong> &nbsp;•&nbsp; R$ {pedido['valor']:,.2f}
            </div>
            <div style="color:#a8c0d3; font-size:0.86rem; margin-top:0.25rem;">
                📦 {pedido['itens']}
            </div>
            <div class="progress-bar-wrap">
                <div class="{progress_class}"></div>
            </div>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-dot dot-gold"></div>
                    Chegada: {_formatar_hora(pedido['horario_chegada'])}
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot {'dot-green' if pedido['inicio_preparacao'] else 'dot-gray'}"></div>
                    Início: {_formatar_hora(pedido['inicio_preparacao'])}
                </div>
                <div class="timeline-item">
                    <div class="timeline-dot {'dot-blue' if pedido['fim_preparacao'] else 'dot-gray'}"></div>
                    Fim: {_formatar_hora(pedido['fim_preparacao'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Botões de ação ──
        # Encontrar o índice real na lista original
        real_idx = st.session_state.fila_preparando.index(pedido)

        if status == "aguardando":
            if st.button("▶️ Iniciar Preparação", key=f"iniciar_{pedido['pedido_id']}"):
                st.session_state.fila_preparando[real_idx]["status"] = "preparando"
                st.session_state.fila_preparando[real_idx]["inicio_preparacao"] = datetime.now().isoformat()
                st.rerun()

        elif status == "preparando":
            if st.button("✅ FIM DE PREPARAÇÃO", key=f"fim_{pedido['pedido_id']}", type="primary"):
                agora = datetime.now().isoformat()
                pedido_finalizado = dict(st.session_state.fila_preparando[real_idx])
                pedido_finalizado["status"] = "pronto"
                pedido_finalizado["fim_preparacao"] = agora
                pedido_finalizado["horario_pronto"] = agora

                # Move para fila de entrega
                st.session_state.fila_entrega.append(pedido_finalizado)
                st.session_state.fila_preparando.pop(real_idx)
                st.success(f"Pedido **{pedido['pedido_id']}** enviado para Entrega!", icon="🚀")
                st.rerun()


def _render_tab_entrega():
    """Tab 2 — Fila de entrega ordenada por horário de preparo concluído."""
    fila = st.session_state.fila_entrega

    if not fila:
        st.info("Nenhum pedido pronto para entrega no momento.")
        return

    # Ordena por horário que ficou pronto (ordem de chegada na fila de entrega)
    fila_sorted = sorted(fila, key=lambda p: p.get("horario_pronto", ""))

    st.markdown(f"**{len(fila_sorted)} pedido(s) na fila de entrega**")
    st.markdown("---")

    # Exibe em 3 colunas
    cols = st.columns(3)

    for i, pedido in enumerate(fila_sorted):
        col = cols[i % 3]

        with col:
            st.markdown(f"""
            <div class="entrega-card">
                <div style="font-weight:700; color:#fff; font-size:0.95rem;">
                    🧾 {pedido['pedido_id']}
                </div>
                <div style="color:#a8c0d3; font-size:0.82rem; margin-top:0.15rem;">
                    Pronto às {_formatar_hora(pedido.get('horario_pronto'))}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"📋 Detalhes — {pedido['cliente']}", expanded=False):
                st.write(f"**Cliente:** {pedido['cliente']}")
                st.write(f"**WhatsApp:** {pedido['whatsapp']}")
                st.write(f"**Endereço:** {pedido['endereco']}")
                st.write(f"**Itens:** {pedido['itens']}")
                st.write(f"**Valor:** R$ {pedido['valor']:,.2f}")
                st.markdown("---")
                st.write(f"⏰ Chegada: {_formatar_dt(pedido['horario_chegada'])}")
                st.write(f"🔥 Início preparo: {_formatar_dt(pedido['inicio_preparacao'])}")
                st.write(f"✅ Pronto: {_formatar_dt(pedido['fim_preparacao'])}")

                st.markdown("---")

                # Selecionar entregador
                entregadores_ativos = [
                    e for e in st.session_state.get("entregadores", []) if e["status"] == "Ativo"
                ]
                nomes_entregadores = [e["nome"] for e in entregadores_ativos]

                if nomes_entregadores:
                    entregador_sel = st.selectbox(
                        "Entregador",
                        nomes_entregadores,
                        key=f"sel_ent_{pedido['pedido_id']}",
                    )
                    if st.button("🏍️ Confirmar Saída", key=f"sair_{pedido['pedido_id']}"):
                        agora = datetime.now()
                        registro = dict(pedido)
                        registro["entregador"] = entregador_sel
                        registro["data_saida"] = agora.strftime("%d/%m/%Y")
                        registro["horario_saida"] = agora.strftime("%H:%M:%S")
                        registro["status"] = "em_entrega"

                        st.session_state.historico_entregas.append(registro)

                        # Remove da fila de entrega
                        real_idx = st.session_state.fila_entrega.index(pedido)
                        st.session_state.fila_entrega.pop(real_idx)
                        st.success(f"Pedido **{pedido['pedido_id']}** saiu com **{entregador_sel}**!", icon="🏍️")
                        st.rerun()
                else:
                    st.warning("Nenhum entregador ativo cadastrado. Cadastre na página Entregador.")


def _render_tab_entregador():
    """Tab 3 — Registro de entregas com dados do entregador em dataframe."""
    historico = st.session_state.historico_entregas

    if not historico:
        st.info("Nenhuma entrega registrada ainda. Confirme saídas na aba Entrega.")
        return

    st.subheader("📊 Registro de Entregas")

    # Monta DataFrame
    dados = []
    for reg in historico:
        # Busca perfil do entregador
        ent_data = next(
            (e for e in st.session_state.get("entregadores", []) if e["nome"] == reg.get("entregador")),
            None,
        )

        dados.append({
            "Pedido": reg.get("pedido_id", ""),
            "Cliente": reg.get("cliente", ""),
            "Valor (R$)": f"R$ {reg.get('valor', 0):,.2f}",
            "Entregador": reg.get("entregador", ""),
            "Moto": ent_data["modelo_moto"] if ent_data else "—",
            "Data Saída": reg.get("data_saida", ""),
            "Horário Saída": reg.get("horario_saida", ""),
            "Endereço": reg.get("endereco", ""),
        })

    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Cards dos entregadores envolvidos
    st.markdown("---")
    st.subheader("🏍️ Entregadores em Rota")

    entregadores_em_rota = list({reg.get("entregador") for reg in historico if reg.get("entregador")})

    if entregadores_em_rota:
        cols = st.columns(min(len(entregadores_em_rota), 3))
        for i, nome_ent in enumerate(entregadores_em_rota):
            ent_data = next(
                (e for e in st.session_state.get("entregadores", []) if e["nome"] == nome_ent),
                None,
            )
            if not ent_data:
                continue

            entregas_ent = [r for r in historico if r.get("entregador") == nome_ent]

            with cols[i % 3]:
                st.markdown(f"""
                <div class="entrega-card" style="text-align:center;">
                    <img src="{ent_data.get('perfil_img', '')}" style="width:56px;height:56px;border-radius:50%;border:2px solid rgba(120,255,182,0.3);margin-bottom:0.5rem;" alt="{nome_ent}">
                    <div style="font-weight:700;color:#fff;">{nome_ent}</div>
                    <div style="font-size:0.84rem;color:#a8c0d3;">🏍️ {ent_data.get('modelo_moto','')}</div>
                    <div style="font-size:0.84rem;color:#7af0b0;margin-top:0.3rem;">📦 {len(entregas_ent)} entrega(s)</div>
                </div>
                """, unsafe_allow_html=True)


def showPreparacao():
    st.title("🍳 Preparação & Entrega")
    st.markdown("Gerencie o fluxo de preparação e entrega dos pedidos do Chef Delivery.")

    _init_preparacao_state()

    # Injeta CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # Métricas rápidas
    total_prep = len(st.session_state.fila_preparando)
    total_entrega = len(st.session_state.fila_entrega)
    total_saiu = len(st.session_state.historico_entregas)

    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Em Preparação", total_prep)
    c2.metric("📦 Prontos p/ Entrega", total_entrega)
    c3.metric("🏍️ Saíram p/ Entrega", total_saiu)

    st.markdown("---")

    # ── TABS ──
    tab_prep, tab_entrega, tab_entregador = st.tabs([
        "🔥 Preparando",
        "📦 Entrega",
        "🏍️ Entregador",
    ])

    with tab_prep:
        _render_tab_preparando()

    with tab_entrega:
        _render_tab_entrega()

    with tab_entregador:
        _render_tab_entregador()
