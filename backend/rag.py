import fitz
import prompts
import os
import numpy as np
from openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
from chunks import get_semantic_chunks
from vectorstore import initialize_chroma
from embeddings import get_hf_embeddings

load_dotenv()

client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_KEY')
        )

chat_memory = []

texts = []

def call_openai(prompt):
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

def retrieve_relevant_documents(query, top_k=5):
    chromadb = initialize_chroma()
    embedded_query = get_hf_embeddings().embed_query(query)
    results = chromadb.similarity_search(embedded_query, k=top_k)
    return [doc.page_content for doc in results]


def ask_the_chatbot(query):
    relevant_docs = retrieve_relevant_documents(query)
    
    context = "\n".join(relevant_docs)

    if not context:
        yield "No relevant documents found."
        return
    
    prompt = prompts.get_full_rag_prompt(context, query)

    for chunk in call_openai(prompt):
        yield chunk
