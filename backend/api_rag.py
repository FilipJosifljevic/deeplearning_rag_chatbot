import os
import prompts
import rag
import threading
import json
from vectorstore import load_pdfs_from_directory, add_new_pdf_to_chroma, load_faiss
from load_and_clean_text import extract_text_from_pdf
from chunks import get_recursively_split_chunks, get_recursively_split_chunks_bigger
from fastapi import Request
from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, HTMLResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

frontend_files_path = os.path.join(os.getcwd(), "frontend", "frontend-rag-deep-learning-chatbot", "browser")

app.mount('/static', StaticFiles(directory=frontend_files_path, html=True), name='static')

#@app.get("/{full_path:path}")
#async def catch_all(full_path: str):
#    excluded_routes = ["chat", "query", "upload", "documents"]
#    if full_path and any(full_path.startswith(route) for route in excluded_routes):
#        return HTTPException(status_code=404, detail="API Route not found")
#    return FileResponse(f"{frontend_files_path}/index.html")

class QueryRequest(BaseModel):
    query: str

DOCUMENTS_DIR = "/workspace/documents"

# Automatically load all documents from the folder into the ChromaDB on startup
@app.on_event("startup")
async def load_existing_documents():
    try:
        # Create the folder if it doesn't exist
        if not os.path.exists(DOCUMENTS_DIR):
            os.makedirs(DOCUMENTS_DIR)

        #initialize_chroma()
        load_pdfs_from_directory(DOCUMENTS_DIR)

    except Exception as e:
        print(f"Error loading documents: {str(e)}")

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(DOCUMENTS_DIR, file.filename)
        
        # Save the uploaded file to the folder
        with open(file_location, "wb") as f:
            f.write(await file.read())

        uploaded_documents = []
        processed_text = extract_text_from_pdf(file_location)
        processed_chunks = get_recursively_split_chunks(processed_text)
        processed_chunks_bigger = get_recursively_split_chunks_bigger(processed_text)
        uploaded_chunks = processed_chunks + processed_chunks_bigger
        uploaded_documents.extend(uploaded_chunks)
        faiss_vectorstore = load_faiss()
        faiss_vectorstore.add_documents(documents=uploaded_documents)

        return {"message": f"File '{file.filename}' successfully added to FAISS index"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.post("/api/query/")
async def query_rag_chatbot(request: QueryRequest):
    query=request.query
    try:
        return StreamingResponse(rag.openai_response(query), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/api/documents/")
async def get_documents():
    try:
        documents = [f for f in os.listdir(DOCUMENTS_DIR) if os.path.isfile(os.path.join(DOCUMENTS_DIR, f))]
        doc_names = [doc.rsplit('.', 1)[0] for doc in documents]
        return doc_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving a list of uploaded documents : {str(e)}")

@app.get("/")
async def redirect_to_chat():
    return RedirectResponse(url="/chat")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    file_path = os.path.join(frontend_files_path, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    return FileResponse(f"{frontend_files_path}/index.html")


