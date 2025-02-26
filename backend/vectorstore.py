import os
import glob
import pymupdf4llm
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from embeddings import get_hf_embeddings
from chunks import get_semantic_chunks, get_recursively_split_chunks

chromadb = None

chroma_path = "/workspace/chromadb"

def initialize_chroma():
    global chromadb
    if chromadb is None:
        chromadb = Chroma(persist_directory=chroma_path, embedding_function=get_hf_embeddings())
        print("ChromaDB initialized!")
    return chromadb

def chunk_and_store_documents(docs, metadatas=None):
    global chromadb
    if chromadb is None:
        initialize_chroma()

    chunks = get_semantic_chunks(docs)

    chromadb.add_documents(chunks)

    print(f"Added {len(chunks)} documents to ChromaDB.")

def load_pdfs_from_directory(directory: str):
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    documents = []

    for pdf_path in pdf_files:
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = pdf_path  # Add source metadata
        documents.extend(docs)

    if documents:
        chunk_and_store_documents(documents)
        print(f"Loaded and stored {len(documents)} documents from {directory}.")

def add_new_pdf_to_chroma(file_path: str):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()

    for doc in docs:
        doc.metadata["source"] = file_path

    chunk_and_store_documents(docs)
    print(f"Added {len(docs)} chunks from '{file_path}' to ChromaDB.")
