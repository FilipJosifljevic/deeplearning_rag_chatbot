import fitz
import prompts
import os
import time
import numpy as np
import queue
import threading
import logging
import asyncio
import json
from fastapi import WebSocket
from typing import AsyncGenerator
from openai import OpenAI
from fastapi.responses import StreamingResponse
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFDirectoryLoader
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
from chunks import get_semantic_chunks
from vectorstore import load_faiss
from embeddings import get_hf_embeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv()

client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_KEY')
        )

chat_memory = []

texts = []

async def openai_response(query: str):
    try:
        relevant_docs = retrieve_relevant_documents(query)
        formatted_context = prompts.format_chunks(relevant_docs)
        system_prompt = prompts.get_full_english_rag_prompt(formatted_context)

        chat_memory = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        full_response = ""

        for chunk in client.chat.completions.create(model="llama3.1", messages=chat_memory, stream=True,):
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
        
        chat_memory.append({"role": "system", "content": full_response})

    except Exception as e:
        yield f"Error : {str(e)}"

def retrieve_relevant_documents(query, top_k=10):
    #chromadb = initialize_chroma()
    #embedded_query = get_hf_embeddings().embed_query(query)
    #results = chromadb.similarity_search(query, k=top_k)
    faiss_vectorstore = load_faiss()
    results = faiss_vectorstore.similarity_search(query, top_k)
    #return rerank_with_sbert(query, results)
    return [doc.page_content for doc in results]

def rerank_with_sbert(query, results):
    query_embedding = sbert_model.encode(query, convert_to_tensor=True)
    doc_embeddings = sbert_model.encode([doc.page_content for doc in results], convert_to_tensor=True)

    scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

    sorted_results = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [doc.page_content for doc, _ in sorted_results]

def call_openai_for_eval(query):
    relevant_docs = retrieve_relevant_documents(query)
    context = "\n\n".join(relevant_docs)
    prompt = prompts.get_full_english_rag_prompt(context, query)

    chat_memory.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama3.1",
        messages=chat_memory,
        stream=True
    )

    return response

