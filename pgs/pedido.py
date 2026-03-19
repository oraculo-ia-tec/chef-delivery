
import streamlit as st
import asyncio

def inicializar_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "primeiro_nome" not in st.session_state:
        st.session_state["primeiro_nome"] = ""

def atualizar_primeiro_nome(nome_completo):
    if nome_completo:
        st.session_state["primeiro_nome"] = nome_completo.split()[0]
    else:
        st.session_state["primeiro_nome"] = ""

async def showPedido():
    st.title("Pedidos - Chef Delivery")
    st.write("Faça seu pedido ou tire dúvidas com nosso assistente!")

    inicializar_session_state()

    # Exibe o histórico
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        else:
            st.markdown(f"**ChefBot:** {msg['content']}")

    user_input = st.text_input("Digite sua mensagem ou pedido:", "")
    if st.button("Enviar") and user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        # Aqui você pode integrar com Groq futuramente
        resposta = f"Olá! Sou o assistente ChefBot. Como posso ajudar no seu pedido hoje? (Simulação)"
        st.session_state["messages"].append({"role": "assistant", "content": resposta})
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Resumo do Pedido")
    if st.session_state["messages"]:
        pedidos = [msg["content"] for msg in st.session_state["messages"] if msg["role"] == "user"]
        st.write("\n".join(pedidos))
    else:
        st.write("Nenhum pedido realizado ainda.")
