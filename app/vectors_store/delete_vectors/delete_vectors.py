from dotenv import load_dotenv, find_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain.indexes import index

from app.vectors_store.utilities.utilities import get_qdrant_vectorstore_client, get_qdrant_langchain_client, get_record_manager_client

from qdrant_client.http import models as rest

load_dotenv(find_dotenv())

def delete_all_vectors(index_name: str = "random_index_name"):
        
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    client = get_qdrant_vectorstore_client()
    
    if not client.collection_exists(collection_name=index_name):
        client.create_collection(
            collection_name=index_name,
            vectors_config= {
                index_name: rest.VectorParams(
                    distance=rest.Distance.COSINE,
                    size=1536,
                ),
            },
        )
        
    vectorstore = get_qdrant_langchain_client(index_name=index_name, embedding=embedding, vector_name=index_name)
    
    record_manager = get_record_manager_client(index_name=index_name)
    
    indexing_stats = index(
        [],
        record_manager,
        vectorstore,
        cleanup="full",
        source_id_key="source",
        )
    
    print("----- ALL FILES DELETED -----")
    
    return indexing_stats

   