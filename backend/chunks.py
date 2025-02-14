from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

hf_embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-mpnet-base-v2',
        model_kwargs={'device' : 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
        )

semantic_chunker = SemanticChunker(hf_embeddings)

def get_semantic_chunks(text):
    docs = semantic_chunker.create_documents([text])
    return docs


