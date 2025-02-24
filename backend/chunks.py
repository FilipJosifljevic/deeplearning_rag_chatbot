from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

hf_embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-mpnet-base-v2',
        model_kwargs={'device' : 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
        )

semantic_chunker = SemanticChunker(hf_embeddings, breakpoint_threshold_type="percentile")
markdown_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=100)

def get_semantic_chunks(docs):
    print(f"Processing {len(docs)} documents for chunking...")
    docs = semantic_chunker.create_documents([d.page_content for d in docs])
    return docs

def get_markdown_chunks(text):
    return markdown_splitter.create_documents([text])
