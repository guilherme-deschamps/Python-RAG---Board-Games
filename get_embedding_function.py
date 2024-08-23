from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding_function():
    """Gets an embedding function from Langchain.
    This function returns an embedding function provided by Amazon, but it can also be done
    using local embedding models.

    Returns:
        _type_: Embedding function provided by Bedrock (Amazon).
    """
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    return embeddings