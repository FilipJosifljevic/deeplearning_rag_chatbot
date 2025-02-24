import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": os.getenv("EMBEDDINGS_DEVICE")}
encode_kwargs = {"normalize_embeddings": True}

def get_hf_embeddings():
    return HuggingFaceEmbeddings( model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

