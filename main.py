from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
CAMINHO_DB = "db"

prompt_template = """
Responda a pergunta do usuário: {pergunta}

Com base nessas informações: 

{base_conhecimento}
"""

pergunta = input("Escreva a sua pergunta: ")

# carregar o banco de dados

funcao_embedding = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", task_type="retrieval_query")
db = Chroma(persist_directory=CAMINHO_DB, embedding_function=funcao_embedding)

# comparar a pergunta do usuario (embedding) com o meu banco de  dados

resultados = db.similarity_search