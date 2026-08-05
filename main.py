from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
CAMINHO_DB = "db"

prompt_template = """
Responda a pergunta do usuário: {pergunta}

Com base nessas informações: 

{base_conhecimento}
"""

def perguntar():
  pergunta = input("Escreva a sua pergunta: ")

  # carregar o banco de dados

  funcao_embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2", task_type="QUESTION_ANSWERING")
  db = Chroma(persist_directory=CAMINHO_DB, embedding_function=funcao_embedding)

  # comparar a pergunta do usuario (embedding) com o meu banco de  dados

  resultados = db.similarity_search_with_relevance_scores(pergunta, k=3)

  # construir prompt

  textos_resultados = []

  for resultado in resultados:
    texto = resultado[0].page_content
    textos_resultados.append(texto)

  base_conhecimento = "\n\n-----\n\n".join(textos_resultados)
  prompt = ChatPromptTemplate.from_template(prompt_template)
  prompt = prompt.invoke({"pergunta": pergunta, "base_conhecimento": base_conhecimento})

  # chamar o modelo de llm

  modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
  texto_resposta = modelo.invoke(prompt).content[0]["text"]

  print(f"\n\nResposta da IA: {texto_resposta}")

perguntar()