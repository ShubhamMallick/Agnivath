"""
Sales Lead Qualification Assistant - Main Application
FastAPI application for lead processing and qualification
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routes.leads import router as leads_router
from app.routes.assistant import router as assistant_router

# Get the source-code directory (where run.py is)
source_code_dir = Path(__file__).parent.parent

app = FastAPI(
    title="Sales Lead Qualification Assistant",
    description="AI-powered lead qualification system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from source-code/static
app.mount("/static", StaticFiles(directory=str(source_code_dir / "static")), name="static")

# Include routers
app.include_router(leads_router)
app.include_router(assistant_router)


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the dashboard"""
    html_path = source_code_dir / "static" / "index.html"
    
    if not html_path.exists():
        return f"""
        <h1>Sales Lead Qualification Assistant</h1>
        <p>Dashboard not found.</p>
        <p>Looking for: {html_path}</p>
        """
    
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error loading dashboard</h1><p>{str(e)}</p>"


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Sales Lead Qualification Assistant",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080
    )
