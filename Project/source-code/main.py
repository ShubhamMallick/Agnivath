from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from rag import RAGSystem
from pydantic import BaseModel
import os

app = FastAPI()
rag = RAGSystem()

class QueryRequest(BaseModel):
    query: str
    provider: str = "openrouter"  # Default to openrouter

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = f"../documents/{file.filename}"
    os.makedirs("../documents", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    documents = rag.load_document(file_path)
    chunks = rag.split_documents(documents)
    rag.create_vector_store(chunks)
    rag.create_qa_chain()
    
    return {"message": "Document uploaded and processed successfully"}

@app.post("/query")
def query(request: QueryRequest):
    result = rag.query(request.query, request.provider)
    return {"answer": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
