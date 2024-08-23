import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma

DATA_PATH = "./data/"
CHROMA_PATH = "./chroma/"

def main():
    # Checks if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("--- Clearing Database ---")
        clear_database()
    
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)
    
def load_documents():
    """Loads all PDF documents from the DATA_PATH folder.

    Returns:
        _type_: List of documents loaded.
    """
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    '''
    Function to split the pages of documents into smaller chunks.
    
    Parameter: 
        documents: list of 'Document' type.
    '''
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    """
    Creates / connects to the ChromaDB, calculates chunk IDs and adds the chunks to the ChromaDB.
    It only adds documents that were not previously on the database.

    Args:
        chunks (list[Document]): List of chunks to be added.
    """
    # Open ChromaDB connection
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )
    
    # Calculate chunk IDs
    chunks_with_ids = calculate_chunk_ids(chunks)
    
    existing_items = db.get(include=[])
    existing_ids = set(existing_items['ids'])
    print(f"Number of existing documents in DB: {len(existing_ids)}")
    
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
        
    # Checks if there are any new chunks
    if len(new_chunks):
        print(f"👉  Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add!")
    
def calculate_chunk_ids(chunks: list[Document]):
    """
    This function creates IDs like "data/monopoly.pdf:0:1"
    Page Source : Page Number : Chunk Index
    """
    last_page_id = None
    current_chunk_index = 0
    
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        
        # If the page ID is the same as the last one, incerment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
        
        # Calculate chunk id
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        
        # Add id to chunk metadata
        chunk.metadata['id'] = chunk_id
        
    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        
if __name__ == "__main__":
    main()
            