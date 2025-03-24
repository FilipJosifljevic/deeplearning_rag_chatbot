import fitz
import prompts
import os
import time
import numpy as np
import queue
import threading
import logging
import asyncio
from typing import AsyncGenerator
from openai import OpenAI
from fastapi.responses import StreamingResponse
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFDirectoryLoader
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
from chunks import get_semantic_chunks
from vectorstore import initialize_chroma
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

data_streaming_started = threading.Event()
response_queue = queue.Queue()
error_queue = queue.Queue()

def heartbeat_task():
    while not data_streaming_started.is_set():
        yield "[heartbeat]\n"
        time.sleep(1)


def openai_response_thread(query):
    try:
        relevant_docs = retrieve_relevant_documents(query)
        context = "\n\n".join(relevant_docs)
        prompt = prompts.get_full_english_rag_prompt(context, query)

        chat_memory.append({"role": "user", "content": prompt})

        full_response = ""

        response = client.chat.completions.create(
                model="llama3.1",
                messages=chat_memory,
                stream=True
                )

        full_response = ""

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text

                if not data_streaming_started.is_set():
                    data_streaming_started.set()

                response_queue.put(text)

        response_queue.put(None)

        chat_memory.append({"role": "assistant", "content": full_response})

    except Exception as e:
        logger.error(f"Error in OpenAI response thread : {str(e)}")
        error_queue.put(str(e))
        response_queue.put(None)

def generate_streaming_response(query):
    data_streaming_started.clear()

    openai_thread = threading.Thread(target=openai_response_thread, args=(query, ), daemon=True)
    openai_thread.start()

    for heartbeat in heartbeat_task():
        yield "data : [heartbeat]\n"

        try:
            error = error_queue.get_nowait()
            yield error
            return
        except queue.Empty:
            pass

    while True:
        try:
            chunk = response_queue.get()
            if chunk is None:
                    break
            yield chunk
        except queue.Empty:
            yield "data: Error : response timeout"
            break
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
            break

def retrieve_relevant_documents(query, top_k=10):
    chromadb = initialize_chroma()
    #embedded_query = get_hf_embeddings().embed_query(query)
    results = chromadb.similarity_search(query, k=top_k)

    return rerank_with_sbert(query, results)
    #return [doc.page_content for doc in results]

def rerank_with_sbert(query, results):
    query_embedding = sbert_model.encode(query, convert_to_tensor=True)
    doc_embeddings = sbert_model.encode([doc.page_content for doc in results], convert_to_tensor=True)

    scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

    sorted_results = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [doc.page_content for doc, _ in sorted_results]


