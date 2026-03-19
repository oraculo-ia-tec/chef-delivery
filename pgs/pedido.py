import streamlit as st
import openai
import os
import time
import pandas as pd

# Função para exibir a página de pedidos com chatbot
def showPedido():
    st.title("Pedidos - Chef Delivery")
    st.write("Faça seu pedido ou tire dúvidas com nosso assistente!")

    # Histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Exibe o histórico
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        else:
            st.markdown(f"**ChefBot:** {msg['content']}")

    # Campo de entrada do usuário
    user_input = st.text_input("Digite sua mensagem ou pedido:", "")
    if st.button("Enviar") and user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        # Chamada ao modelo de linguagem (simulação ou integração real)
        response = gerar_resposta_chatbot(user_input)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Resumo do Pedido")
    if st.session_state["messages"]:
        pedidos = [msg["content"] for msg in st.session_state["messages"] if msg["role"] == "user"]
        st.write("\n".join(pedidos))
    else:
        st.write("Nenhum pedido realizado ainda.")

# Função simulada para gerar resposta do chatbot
def gerar_resposta_chatbot(mensagem):
    # Aqui você pode integrar com Groq, OpenAI, etc.
    # Exemplo simples:
    if "carne" in mensagem.lower():
        return "Temos picanha, alcatra, fraldinha e muito mais! Qual corte deseja?"
    elif "entrega" in mensagem.lower():
        return "Entregamos em toda a região de Mantiqueira. Qual o seu endereço?"
    elif "preço" in mensagem.lower() or "valor" in mensagem.lower():
        return "Os preços variam conforme o corte e quantidade. Deseja consultar algum produto específico?"
    else:
        return "Olá! Sou o assistente ChefBot. Como posso ajudar no seu pedido hoje?"
