import os
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client

def get_vector_store(config, embedding_function):
    """
    Get a vector store based on the configuration.
    
    Args:
        config: Configuration dictionary containing vector store settings
        embedding_function: Embedding function to use for the vector store
    
    Returns:
        A vector store instance
    """
    vector_store_type = config.get("type", "").lower()
    
    if vector_store_type == "supabase":
        supabase_url = config.get("supabase_url")
        supabase_key = config.get("supabase_key")
        table_name = config.get("table_name", "embeddings")
        
        # Create Supabase client
        supabase_client = create_client(supabase_url, supabase_key)
        
        # Return Supabase vector store
        return SupabaseVectorStore(
            client=supabase_client,
            embedding=embedding_function,
            table_name=table_name,
        )
    else:
        raise ValueError(f"Unsupported vector store type: {vector_store_type}")
