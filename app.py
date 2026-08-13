import streamlit as st
import time
from main import perguntar


def app():
  st.header("Board games Chatbot", divider=True)
  st.write('Jogos disponíveis: Cascadia, Coup, Cangaço e Trio')

  mensagem_usuario = st.chat_input("Digite aqui a sua mensagem")

  if mensagem_usuario:
    if "mensagens" in st.session_state:
      mensagens = st.session_state["mensagens"]
    else:
      mensagens = []
      st.session_state["mensagens"] = mensagens

    mensagens.append({"usuario": "user", "texto": mensagem_usuario})

    carregar_mensagens(mensagens)

    with st.status("Perguntando para a AI ..."):
      base_conhecimento, texto_resposta = perguntar(mensagem_usuario)

    # mensagens.append({"usuario": "assistant", "texto": base_conhecimento}) # para visualizar os chunks retornados pela base vetorizada

    # carregar_mensagens(mensagens)

    mensagens.append({"usuario": "ai", "texto": texto_resposta})

    carregar_mensagens(mensagens[-1:], stream=True)

def stream_resposta(resposta):
  for palavra in resposta.split(" "):
    yield palavra + " "
    time.sleep(0.02)

def carregar_mensagens(mensagens, stream=False):
  for mensagem in mensagens:
    if mensagem["usuario"] == "ai" and stream == True:
      with st.chat_message(mensagem["usuario"]):
                st.write_stream(stream_resposta(mensagem["texto"]))
    else:
      with st.chat_message(mensagem["usuario"]):
            st.write(mensagem["texto"])

app()