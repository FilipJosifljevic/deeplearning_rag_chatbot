import os
import prompts
import rag
from vectorstore import initialize_chroma, load_pdfs_from_directory, add_new_pdf_to_chroma
from fastapi import Request
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
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

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    if full_path and full_path not in ["chat", "upload"]:
        return FileResponse(f"{frontend_files_path}/{full_path}")
    return FileResponse(f"{frontend_files_path}/index.html")

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

        initialize_chroma()
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

        add_new_pdf_to_chroma(file_location)

        return {"message": f"File '{file.filename}' successfully added to ChromaDB"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.post("/api/query/")
async def query_rag_chatbot(request: QueryRequest):
    query = request.query
    try:
        
        stream_generator  = rag.call_openai(query)

        #return {"response": list(stream_generator)}
        return StreamingResponse(stream_generator, media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

