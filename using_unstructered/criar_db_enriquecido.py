import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from dotenv import load_dotenv
import time

load_dotenv()

def criar_db():
   
  pasta = Path("./documentos_json")

  vectorstore = criar_vectorstore()

  for caminho in pasta.glob("*.json"):
    
    with open(caminho, encoding='utf-8') as arquivo:
      documento_json = json.load(arquivo)

    conteudo_raiz = extrair_conteudo_raiz_paginas(documento_json)
    conteudo_formatado = formatar_paginas_llm(conteudo_raiz)
    chunks = criar_chunks(conteudo_formatado, caminho.name[:-5])
    vetorizar_novos_chunks(vectorstore, chunks)


# extrair conteudo por páginas
def extrair_conteudo_raiz_paginas(documento_json):
  conteudo_raiz_paginas = []

  numero_pagina = documento_json[0]['metadata']['page_number']
  conteudo_pagina = ''

  for item in documento_json:

    if item['metadata']['page_number'] == numero_pagina:
      conteudo_pagina += (f"{item['type']}: {item['text']} \n\n-----\n\n")
    else:

      conteudo_raiz_paginas.append({
        'pagina': numero_pagina,
        'texto': conteudo_pagina
      })

      conteudo_pagina = ''
      numero_pagina = item['metadata']['page_number']
      
  conteudo_raiz_paginas.append({
            'pagina': numero_pagina,
            'texto': conteudo_pagina
  })

  return conteudo_raiz_paginas

# passar para a AI uniformizar e criar descrição
def formatar_paginas_llm(paginas):

  conteudo_limpo_paginas = []
  counter = 0

  for pagina in paginas:

    counter += 1
    print(f'Passando o documento de n°{counter} para o gemini formatar')

    if (counter % 5) == 0:
       time.sleep(30)

    prompt_template = """
    Fiz a leitura de um PDF usando a biblioteca Unstructured para python. Formate o conteúdo que vou te passar separando sempre entre texto (unificar quando tiver pedaços seguidos mas separados por elementos diferentes), imagem (traduzir a descrição feita para o português) ou tabela (se tiver).

    Ex: "Texto: exemploexemplo... (pular linha) Imagem: exemploexemplo..."

    NÃO adicione outros textos seus, como "aqui está o resultado..." ou "conteúdo insuficiente"
    FAÇA modificações na ordem do texto se você ver necessidade ou correções de palavras, mas não adicione nada além.

    Conteúdo carregado pelo Unstructred: {conteudo}
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    prompt = prompt.invoke({"conteudo": pagina['texto']})

    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    texto_resposta = modelo.invoke(prompt).content[0]["text"]

    conteudo_limpo_paginas.append({
      'pagina': pagina['pagina'],
      'texto': texto_resposta
    })

  return conteudo_limpo_paginas

# criar os chunks com 500 caracteres do anterior + 500 do próximo
def criar_chunks(paginas, nome_jogo):

  chunks = []

  for i, pagina in enumerate(paginas):

    texto_atual = pagina["texto"]

    # 500 caracteres finais da página anterior
    if i > 0:
        contexto_anterior = paginas[i - 1]["texto"][-500:]
    else:
        contexto_anterior = ""

    # 500 caracteres iniciais da página seguinte
    if i < len(paginas) - 1:
        contexto_posterior = paginas[i + 1]["texto"][:500]
    else:
        contexto_posterior = ""

    texto_chunk = f"""
    [DESCRIÇÃO]
    Esse chunk faz parte do manual do jogo {nome_jogo}

    [CONTEXTO - PÁGINA ANTERIOR]
    {contexto_anterior}

    [PÁGINA {pagina["pagina"]}]
    {texto_atual}

    [CONTEXTO - PÁGINA POSTERIOR]
    {contexto_posterior}
    """

    chunks.append(
        Document(
            page_content=texto_chunk,
            metadata={
                "pagina": pagina["pagina"],
                "documento": nome_jogo
            }
        )
    )

  return chunks

# criar vectorstore
def criar_vectorstore():
   vectorstore = Chroma(
    collection_name="meus_jogos",
    embedding_function=GoogleGenerativeAIEmbeddings(model="gemini-embedding-2", task_type="RETRIEVAL_DOCUMENT"),
    persist_directory="./chroma_db"
    )

   return vectorstore

# adicionar chunks na vectorstore
def vetorizar_novos_chunks(vectorstore, chunks):
  vectorstore.add_documents(chunks)
  print("Chunks vetorizados e armazenados no banco de dados")

criar_db()