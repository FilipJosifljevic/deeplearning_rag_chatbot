import os
import prompts
import rag
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

# Automatically load all documents from the folder into the FAISS index on startup
@app.on_event("startup")
async def load_existing_documents():
    try:
        documents_folder = "/workspace/documents"
        
        # Create the folder if it doesn't exist
        if not os.path.exists(documents_folder):
            os.makedirs(documents_folder)

        # Get all PDF files in the folder
        pdf_files = [f for f in os.listdir(documents_folder) if f.endswith('.pdf')]

        if not pdf_files:
            print("No PDF files found in the documents folder.")
            return

        # Load existing documents into the FAISS index
        for pdf_file in pdf_files:
            file_location = os.path.join(documents_folder, pdf_file)
            print(f"Loading document from {file_location}")
            loaded_texts = rag.load_documents(file_location)
            print(f"Loaded {len(loaded_texts)} texts from {file_location}")

            # Add documents to the FAISS index and texts list
            if loaded_texts:
                print(f"Adding {len(loaded_texts)} texts to FAISS")
                rag.add_to_faiss(loaded_texts)
                rag.texts.extend(loaded_texts)

        print(f"Loaded {len(rag.texts)} documents into FAISS index.")
        
    except Exception as e:
        print(f"Error loading documents: {str(e)}")

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        documents_folder = "/workspace/documents"
        file_location = os.path.join(documents_folder, file.filename)
        
        # Save the uploaded file to the folder
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        # Reload the new document into the FAISS index
        loaded_texts = rag.load_documents(file_location)
        
        # Add the newly loaded document to the FAISS index
        if loaded_texts:
            rag.add_to_faiss(loaded_texts)
            rag.texts.extend(loaded_texts)

        return {"message": "File uploaded and documents indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.post("/api/query/")
async def query_rag_chatbot(request: QueryRequest):
    query = request.query
    try:
        # Ensure that we have documents loaded in the FAISS index
        if not rag.texts:
            raise HTTPException(status_code=400, detail="No documents available for querying.")
        
        stream_generator  = rag.call_openai(query)

        #return {"response": list(stream_generator)}
        return StreamingResponse(stream_generator, media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

