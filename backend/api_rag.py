import os
import prompts
import rag
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel


app = FastAPI()

class QueryRequest(BaseModel):
    query: str

# Automatically load all documents from the folder into the FAISS index on startup
@app.on_event("startup")
async def load_existing_documents():
    try:
        documents_folder = "documents"
        
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

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        documents_folder = "documents"
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


@app.post("/query/")
async def query_rag_chatbot(request: QueryRequest):
    query = request.query
    try:
        # Ensure that we have documents loaded in the FAISS index
        if not rag.texts:
            raise HTTPException(status_code=400, detail="No documents available for querying.")

        relevant_docs = rag.retrieve_relevant_documents(query)
        print(f"Found {len(relevant_docs)} relevant documents")
        # If no relevant documents are found, return an error
        if not relevant_docs:
            raise HTTPException(status_code=400, detail="No relevant documents found for the query.")
        
        context = "\n".join(relevant_docs)
        prompt = prompts.get_full_rag_prompt(context, query)

        # Call OpenAI to get the answer based on the context
        answer = rag.call_openai(prompt)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

