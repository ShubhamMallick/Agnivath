#!/usr/bin/env python
"""
Run the RAG Chat Assistant server
"""
import sys
from pathlib import Path

# Add source-code to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=False
    )
