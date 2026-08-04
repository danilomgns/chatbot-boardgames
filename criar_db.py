from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
PASTA_DOCUMENTOS = "documentos"

def criar_db():
  documentos = carregar_documentos()
  chunks = criar_chunks(documentos)
  vetorizar_chunks(chunks)

def carregar_documentos():
  carregador = PyPDFDirectoryLoader(PASTA_DOCUMENTOS)
  documentos = carregador.load()

  print(f"{len(documentos)} documento(s) carregado(s) com sucesso")

  return documentos
  

def criar_chunks(documentos):

  separador_documentos = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=500,
    length_function=len,
    add_start_index=True
  )

  chunks = separador_documentos.split_documents(documentos)

  print(f"{len(chunks)} chuncks criados")

  return chunks

def vetorizar_chunks(chunks):
  db = Chroma.from_documents(chunks, GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", task_type="retrieval_document"), persist_directory="db")
  print("Chunks vetorizados e armazenados no banco de dados")

criar_db()
