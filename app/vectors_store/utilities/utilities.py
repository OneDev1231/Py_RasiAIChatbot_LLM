from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant

from langchain.indexes import SQLRecordManager

from langchain_openai import OpenAIEmbeddings

from langchain_core.retrievers import BaseRetriever

from dotenv import load_dotenv, find_dotenv

import os

load_dotenv(find_dotenv())

QDRANT_URL = os.environ["QDRANT_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

RECORD_MANAGER_DB_URL = os.environ["RECORD_MANAGER_DB_URL"]

def get_qdrant_vectorstore_client() -> QdrantClient:
    return QdrantClient(
        url=QDRANT_URL, 
        api_key=QDRANT_API_KEY,
    )
    
    
def get_qdrant_langchain_client(index_name: str, embedding, vector_name: str) -> Qdrant:
    return Qdrant(
        client=get_qdrant_vectorstore_client(),
        collection_name=index_name,
        embeddings=embedding,
        vector_name=index_name,
    )
    
def get_record_manager_client(index_name: str) -> SQLRecordManager:
    record_manager =  SQLRecordManager(
        f"weaviate/{index_name}", db_url=RECORD_MANAGER_DB_URL
    )
    record_manager.create_schema()
    
    return record_manager
    
    
def get_qdrant_retriever(index_name: str) -> BaseRetriever:
    
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
        
    vectorstore = get_qdrant_langchain_client(index_name=index_name, embedding=embedding, vector_name=index_name)
    
    vectorstore_retriever = vectorstore.as_retriever()
    
    return vectorstore_retriever
        