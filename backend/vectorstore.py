import os
import glob
import pymupdf4llm
from langchain.vectorstores import Chroma, FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from embeddings import get_hf_embeddings, get_mxbai_embeddings
from chunks import get_semantic_chunks, get_recursively_split_chunks, get_recursively_split_chunks_bigger
from load_and_clean_text import extract_text_from_pdf

faiss_vectorstore = None
'''chromadb = None

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

    print(f"Added {len(chunks)} documents to ChromaDB.")'''

def initialize_faiss(docs):
    global faiss_vectorstore
    if faiss_vectorstore is None:
        chunks_smaller = get_recursively_split_chunks(docs)
        chunks_bigger = get_recursively_split_chunks_bigger(docs)
        chunks = chunks_smaller + chunks_bigger
        faiss_vectorstore = FAISS.from_documents(documents = chunks, embedding = get_mxbai_embeddings())
        faiss_vectorstore.save_local("/workspace/faiss_index")
        print("FAISS Initialized!")
    return faiss_vectorstore

def load_faiss():
    global faiss_vectorstore
    if faiss_vectorstore is None:
        faiss_vectorstore = FAISS.load_local(
            "/workspace/faiss_index",
            embeddings = get_mxbai_embeddings()
            )
        print("FAISS loaded from local")
    return faiss_vectorstore

def load_pdfs_from_directory(directory: str):
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    documents = []

    for pdf_path in pdf_files:
        processed_text = extract_text_from_pdf(pdf_path)
        documents.append(processed_text)
    '''for pdf_path in pdf_files:
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = pdf_path  # Add source metadata
        documents.extend(docs)'''

    if documents:
        #chunk_and_store_documents(documents)
        initialize_faiss(documents)
        print(f"Loaded and stored {len(documents)} documents from {directory}.")

def add_new_pdf_to_chroma(file_path: str):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()

    for doc in docs:
        doc.metadata["source"] = file_path

    chunk_and_store_documents(docs)
    print(f"Added {len(docs)} chunks from '{file_path}' to ChromaDB.")
