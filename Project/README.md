# RAG Application

A simple Retrieval-Augmented Generation (RAG) application using LangChain, FastAPI, and OpenRouter with a web frontend.

## Setup

1. Create virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r Project/source-code/requirements.txt
```

2. Configure environment variables in `.env` file:
```
OPENROUTER_API_KEY=your_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen3-30b-a3b
```

## Running the Application

```bash
cd Project/source-code
python main.py
```

Open your browser and go to `http://localhost:8000`

## How to Use

1. **Upload Document**: Click "Choose File" and select a PDF or DOCX file, then click "Upload"
2. **Ask Questions**: Enter your question in the text box and click "Ask"
3. **View Answer**: The answer will appear below

## Storage

- **Documents**: Uploaded to `Project/documents/`
- **Vectors**: Stored in `Project/chroma_db/` (created automatically)

## API Endpoints

- `GET /` - Web interface
- `POST /upload` - Upload and process documents
- `POST /query` - Query the RAG system
