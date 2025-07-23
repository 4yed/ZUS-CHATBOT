from fastapi import FastAPI, HTTPException
from .scraper import get_product_names_all
from .vector_store import get_vector_store, search_products
from .text2sql import OutletQueryProcessor
from langchain_openai import AzureChatOpenAI
import os
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()

# Load Azure OpenAI credentials
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

# Main FastAPI app
app = FastAPI()

# API Endpoints
@app.get("/api/products")
def get_products(query: str):
    try:
        results = search_products(vector_store, query)
        # Create a more contextual prompt for question answering
        prompt = f"""Based on the following product information, please answer the user's question.
        
        Product Information:
        - {", ".join(results)}
        
        User's Question:
        - {query}
        
        Answer:
        """
        summary = llm.invoke(prompt)
        return {"summary": summary.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/outlets")
def get_outlets(query: str):
    try:
        result = outlet_processor.process(query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize components
product_names = get_product_names_all()
vector_store = get_vector_store(product_names)
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=AZURE_API_VERSION,
    azure_deployment=AZURE_OPENAI_MODEL,
    api_key=SecretStr(AZURE_API_KEY) if AZURE_API_KEY else None,
    temperature=0.7,
)
outlet_processor = OutletQueryProcessor() 