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
        # Prefer environment variables to avoid hardcoding secrets in config.yaml
        # Common env names: SUPABASE_URL, SUPABASE_KEY (or SUPABASE_ANON_KEY), SUPABASE_SERVICE_ROLE_KEY
        supabase_url = (
            os.getenv("SUPABASE_URL")
            or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            or config.get("supabase_url")
        )
        supabase_key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or os.getenv("SUPABASE_KEY")
            or config.get("supabase_key")
        )
        table_name = config.get("table_name", "embeddings")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) in your .env, or provide supabase_url/supabase_key in config.yaml."
            )

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
