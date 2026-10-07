from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.rag import RAGSystem
import uvicorn

app = FastAPI(title="AI RAG Assistant")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    html_path = Path(__file__).parent.parent / "static" / "index.html"

    if not html_path.exists():
        return """
        <h1>index.html not found</h1>
        <p>Make sure static/index.html exists.</p>
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
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    documents_dir = project_root / "documents"
    chroma_dir = project_root / "chroma_db"
    
    file_path = documents_dir / file.filename
    documents_dir.mkdir(exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    documents = rag.load_document(str(file_path))
    chunks = rag.split_documents(documents)
    rag.create_vector_store(chunks, str(chroma_dir))
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