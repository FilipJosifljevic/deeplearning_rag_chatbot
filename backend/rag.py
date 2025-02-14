import fitz
import faiss
import prompts
import os
import numpy as np
from openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_KEY')
        )
def load_documents(pdf_path):
    doc = fitz.open(pdf_path)
    split_texts = []
    texts = [] 

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        texts.append(page.get_text("text"))
        split_texts.extend(split_text(page.get_text("text")))

    return split_texts

chat_memory = []

model_name="sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': os.getenv('EMBEDDINGS_DEVICE')}
encode_kwargs = {'normalize_embeddings': True}

hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

dimension = 768
index = faiss.IndexFlatL2(dimension)

texts = []

def split_text(text, chunk_size=500, overlap=100):

    splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
            )

    return splitter.split_text(text)

def add_to_faiss(text_chunks):
    global texts
    texts.extend(text_chunks)
    embeddings = hf.embed_documents(text_chunks)
    faiss_embeddings = np.array(embeddings).astype('float32')
    index.add(faiss_embeddings)

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
    query_embedding = hf.embed_query(query)
    query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)
    retrieved_docs = [texts[i] for i in indices[0]] if indices.size > 0 else []
    
    return retrieved_docs


def ask_the_chatbot(query):
    relevant_docs = retrieve_relevant_documents(query)
    
    context = "\n".join(relevant_docs)

    if not context:
        yield "No relevant documents found."
        return
    
    prompt = prompts.get_full_rag_prompt(context, query)

    answer = call_openai(prompt)

    return answer

