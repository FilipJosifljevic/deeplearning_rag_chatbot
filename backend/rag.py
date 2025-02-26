import fitz
import prompts
import os
import numpy as np
import logging
from openai import OpenAI
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

def call_openai(prompt):
    logger.info(f"\nLLM PROMPT : \n{repr(prompt)}\n")

    chat_memory.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama3.1",
        messages=chat_memory,
        stream=True
     )

    def generate():
        full_response = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
        chat_memory.append({"role": "assistant", "content": full_response})

    return generate()

    #return response
    #return assistant_reply

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

def ask_the_chatbot(query):
    relevant_docs = retrieve_relevant_documents(query)

    if not relevant_docs:
        logger.info("No relevant documents found.")
        yield "No relevant documents found."
        return

    context = "\n\n".join(relevant_docs)
    
    logger.info(f"Retrieved context : \n{context}")

    prompt = prompts.get_full_english_rag_prompt(context, query)
    
    logger.info(f"Generated Prompt for LLM:\n{prompt}")

    response_generator = call_openai(prompt)

    for chunk in response_generator:
        yield chunk
