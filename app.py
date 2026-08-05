import app as st
from main import perguntar


def app():
  st.header("Board games Chatbot", divider=True)
  st.write('Jogos disponíveis: cascadia e coup')

  mensagem_usuario = st.chat_input("Digite aqui a sua mensagem")

  if mensagem_usuario:
    if "mensagens" in st.session_state:
      mensagens = st.session_state["mensagens"]
    else:
      mensagens = []
      st.session_state["mensagens"] = mensagens

    mensagens.append({"usuario": "user", "texto": mensagem_usuario})

    base_conhecimento, texto_resposta = perguntar(mensagem_usuario)

    mensagens.append({"usuario": "assistant", "texto": base_conhecimento})
    mensagens.append({"usuario": "ai", "texto": texto_resposta})

    for mensagem in mensagens:
      with st.chat_message(mensagem["usuario"]):
            st.write(mensagem["texto"])

app()