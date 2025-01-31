import fitz
import faiss
import prompts
import os
import numpy as np
from openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_KEY')
        )
def load_documents(pdf_path):
    doc = fitz.open(pdf_path)
    texts = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        texts.append(page.get_text("text"))

    return texts

chat_memory = []

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': os.getenv('EMBEDDINGS_DEVICE')}
encode_kwargs = {'normalize_embeddings': False}

hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

dimension = 768
index = faiss.IndexFlatL2(dimension)

texts = []

def add_to_faiss(texts):
    embeddings = hf.embed_documents(texts)
    faiss_embeddings = np.array(embeddings).astype('float32')
    index.add(faiss_embeddings)

def call_openai(prompt):
    response = client.chat.completions.create(
        model="llama3.1",
        messages=chat_memory + 
        [
            {"role": "user", "content": prompt}
        ]
     )

    assistant_reply = response.choices[0].message.content
    chat_memory.append({"role": "assistant", "content": assistant_reply})

    #return response
    return assistant_reply

def retrieve_relevant_documents(query, top_k=10):
    query_embedding = hf.embed_query(query)
    query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)
    retrieved_docs = [texts[i] for i in indices[0]]
    
    return retrieved_docs


def ask_the_chatbot(query):
    relevant_docs = retrieve_relevant_documents(query)
    
    context = "/n".join(relevant_docs)
    
    prompt = prompts.get_full_rag_prompt(context, query)

    answer = call_openai(prompt)

    return answer

