import os
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()

# Load Azure OpenAI credentials
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")


def get_vector_store(documents):
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION,
        azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        api_key=SecretStr(AZURE_API_KEY),
    )
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.create_documents(documents)
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def search_products(vector_store, query):
    results = vector_store.similarity_search(query, k=5)
    return [result.page_content for result in results] 