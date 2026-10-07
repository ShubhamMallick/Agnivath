from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from rag import RAGSystem
import os
import uvicorn

app = FastAPI(title="AI RAG Assistant")

# Initialize RAG system when the application starts
try:
    rag = RAGSystem()
    print("RAG system initialized successfully.")
except Exception as e:
    rag = None
    print(f"Failed to initialize RAG system: {e}")


class QueryRequest(BaseModel):
    query: str
    provider: str = "groq"


@app.get("/", response_class=HTMLResponse)
def home():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "index.html")

    if not os.path.exists(html_path):
        return """
        <h1>index.html not found</h1>
        <p>Make sure index.html is in the same folder as main.py.</p>
        """

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        return f"<h1>Error loading page</h1><p>{str(e)}</p>"


@app.get("/health")
def health():
    return {
        "status": "running",
        "rag_initialized": rag is not None
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global rag
    if not rag:
        rag = RAGSystem()
    
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

    if rag is None:
        raise HTTPException(
            status_code=500,
            detail="RAG system is not initialized."
        )

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:
        result = rag.query(
            request.query,
            request.provider
        )

        return {
            "answer": result,
            "provider": request.provider
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080
    )