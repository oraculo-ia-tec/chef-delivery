import requests
from datetime import datetime
import streamlit as st
import os


def postar_no_facebook(token, mensagem, midia_url=None, is_video=False):
    url = f"https://graph.facebook.com/v12.0/me/feed"
    payload = {
        'message': mensagem,
        'access_token': token
    }
    if midia_url:
        if is_video:
            payload['description'] = mensagem
            payload['file_url'] = midia_url
        else:
            payload['picture'] = midia_url
    response = requests.post(url, data=payload)
    return response.json()


def postar_no_instagram(token, midia_url, legenda, is_video=False):
    url = f"https://graph.facebook.com/v12.0/me/media"
    payload = {
        'caption': legenda,
        'access_token': token
    }
    if is_video:
        payload['media_type'] = 'VIDEO'
        payload['video_url'] = midia_url
    else:
        payload['media_type'] = 'IMAGE'
        payload['image_url'] = midia_url
    response = requests.post(url, data=payload)
    return response.json()


# Lista para armazenar os posts
posts = []


# Função para adicionar um novo post
def add_post(content, schedule_time, midia_url, is_video=False):
    posts.append({"content": content, "schedule_time": schedule_time, "midia_url": midia_url, "is_video": is_video})


# Função para visualizar o post antes de enviar
def preview_post(post_content, midia_url, is_video=False):
    st.write("### Pré-visualização do Post")
    st.write(post_content)
    if is_video:
        st.video(midia_url)
    else:
        st.image(midia_url)


def postar_face_insta():
    token = st.text_input("Insira seu Token de Acesso:")

    # Usando Markdown para criar um título com ícones
    st.markdown(
        f"<h1 style='color: #FFFFFF; font-size: 24px;'>🚀 Postagens Automáticas no Facebook e Instagram 🚀</h1>",
        unsafe_allow_html=True
    )

    # Organizando data e hora em colunas
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data de Início:")
    with col2:
        hora_inicio = st.time_input("Hora de Início:")

    col3, col4 = st.columns(2)
    with col3:
        data_fim = st.date_input("Data de Fim:")
    with col4:
        hora_fim = st.time_input("Hora de Fim:")

    # Inputs para título e subtítulo
    titulo = st.text_input("Título:")
    subtitulo = st.text_area("Subtítulo:")

    # Escolha entre imagem ou vídeo
    midia_tipo = st.radio("Escolha o tipo de mídia:", ("Imagem", "Vídeo"))

    # Caminho para salvar a mídia
    if midia_tipo == "Imagem":
        uploaded_file = st.file_uploader("Faça upload da imagem", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            # Salvar a imagem no caminho especificado
            save_path = "./src/img/produto/img_camisa.jpg"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            midia_url = save_path
        else:
            midia_url = st.text_input("Ou insira o link da imagem:")
    else:
        uploaded_file = st.file_uploader("Faça upload do vídeo", type=["mp4", "mov"])
        if uploaded_file:
            # Salvar o vídeo no caminho especificado
            save_path = "./src/video/img_camisa.mp4"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            midia_url = save_path
        else:
            midia_url = st.text_input("Ou insira o link do vídeo:")

    # Inputs adicionais
    link = st.text_input("Link:")
    hashtags = st.text_input("Hashtags (separadas por vírgula):")

    # Botão para visualizar o post
    if st.button("Visualizar Post"):
        mensagem = f"{titulo}\n{subtitulo}\n{hashtags}\n{link}"
        preview_post(mensagem, midia_url, is_video=(midia_tipo == "Vídeo"))

    # Botão para adicionar post
    if st.button("Adicionar Post"):
        mensagem = f"{titulo}\n{subtitulo}\n{hashtags}\n{link}"
        schedule_time = datetime.combine(data_inicio, hora_inicio)
        add_post(mensagem, schedule_time, midia_url, is_video=(midia_tipo == "Vídeo"))
        st.success("Post adicionado com sucesso!")

    # Botão para postar
    if st.button("Postar"):
        if posts:
            for post in posts:
                if post["is_video"]:
                    resultado_facebook = postar_no_facebook(token, post["content"], post["midia_url"], is_video=True)
                    resultado_instagram = postar_no_instagram(token, post["midia_url"], post["content"], is_video=True)
                else:
                    resultado_facebook = postar_no_facebook(token, post["content"], post["midia_url"])
                    resultado_instagram = postar_no_instagram(token, post["midia_url"], post["content"])
                st.success(f"Postagem realizada no Facebook: {resultado_facebook}")
                st.success(f"Postagem realizada no Instagram: {resultado_instagram}")
        else:
            st.error("Nenhum post adicionado.")

    # Exibir posts programados
    st.write("### Posts Programados")
    for post in posts:
        st.write(f"**Conteúdo:** {post['content']}")
        st.write(f"**Programado para:** {post['schedule_time'].strftime('%d/%m/%Y %H:%M:%S')}")
        if post["is_video"]:
            st.video(post["midia_url"])
        else:
            st.image(post["midia_url"])