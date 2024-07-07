from langchain_core.tools import tool
from langchain_core.runnables import ensure_config

from app.vectors_store.utilities.utilities import get_qdrant_retriever
@tool
def lookup_info(query: str) -> str:
    """
    Consult the company products and services and return the relevant information.
    Use this when the customer asks about anything related to the companies products or services (prices, availability, options, etc.).
    
    first arg: query that the assistant should search for    
    """
    
    config = ensure_config()  # Fetch from the context
    configuration = config.get("configurable", {})
    index_name = configuration.get("index_name", None)
    
    if not index_name:
        raise ValueError("No index_name configured.")
    retriever = get_qdrant_retriever(index_name=index_name)
    
    try:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return "Error: index not found"