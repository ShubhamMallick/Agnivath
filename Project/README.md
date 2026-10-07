# Sales Lead Qualification Assistant

This project is an AI-powered sales lead qualification prototype built with FastAPI, LangChain, ChromaDB, and LLM APIs. It helps a sales team process website-generated leads automatically by extracting lead details, qualifying them, and recommending the next action.

## Project goal

A company receives leads from website forms, demo requests, pricing inquiries, and resource downloads. The system:

- captures the lead information
- extracts key business fields from the message
- identifies buying intent and urgency
- checks the lead against product and qualification rules
- scores the lead as HIGH, MEDIUM, or LOW
- recommends the next step for the sales team
- shows results in a dashboard

## Tech stack

- Python
- FastAPI
- LangChain
- ChromaDB
- OpenRouter and Groq LLM providers
- RAG retrieval workflow
- HTML/CSS dashboard frontend

## Workflow

1. Submit a lead through the dashboard or `POST /api/leads/ingest`.
2. The selected LLM extracts business details and flags missing information.
3. The qualifier uses sales knowledge from ChromaDB to recommend a score, priority, reasons, product fit, and next action.
4. The dashboard displays the result; medium- and high-priority leads trigger a demo notification.

## AI Assistant and RAG

- Lead qualification knowledge comes from `Project/source-code/data/*.txt` and is stored in `Project/lead_chroma_db`.
- The dashboard conversation uses those sales vectors and leads processed during the current app session.
- The conversation excludes documents from `Project/chroma_db` and omits lead email and phone fields.
- The conversation uses Groq's `openai/gpt-oss-20b` model. Lead processing defaults to Groq; OpenRouter is optional.
- Sample `leads.json` files are not loaded automatically.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/leads/ingest` | Extract, qualify, and store a lead for this session |
| `POST` | `/api/leads/qualify` | Preview qualification without storing |
| `GET` | `/api/leads/list` | List leads from this session |
| `GET` | `/api/leads/{lead_id}` | Get a current-session lead |
| `POST` | `/api/leads/batch-upload` | Process multiple leads |
| `POST` | `/api/assistant/chat` | Ask the sales knowledge-base assistant |
| `GET` | `/health` | Check service status |

## Setup and Run

From the repository root in PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r .\Project\source-code\requirements.txt
```

Set `GROQ_API_KEY` in a local `.env` file, then run:

```powershell
Set-Location .\Project\source-code
python run.py
```

Open `http://127.0.0.1:8080`. Stop an existing server on port 8080 before starting another.

## Tests and Limitations

Run tests from `Project/source-code` with `python -m unittest discover -s tests`.

This is a prototype: processed leads are kept in memory and cleared on restart; human sales staff make final decisions; language detection, authentication, persistent lead storage, and CRM integration are not implemented.

## Repository structure

```text
Agnivath/
├── .env
├── .env.example
├── .gitignore
├── AI_Usage.md
├── test.py
├── Project/
│   ├── README.md
│   ├── chroma_db/                  # Existing main RAG vectors; not used by dashboard chat
│   ├── lead_chroma_db/             # Sales knowledge-base vectors
│   ├── documents/                  # Empty document staging folder
│   ├── knowledge_base/             # Root-level reference copies
│   │   ├── faq.txt
│   │   ├── pricing.txt
│   │   ├── products.txt
│   │   └── qualification_rules.txt
│   ├── sample_data/
│   │   └── leads.json              # Sample leads; not loaded by the app
│   └── source-code/
│       ├── .env                    # Local environment configuration
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── assistant.py
│       │       └── leads.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── lead_processor.py
│       │   ├── lead_qualifier.py
│       │   ├── notifier.py
│       │   └── rag.py
│       ├── data/
│       │   ├── faq.txt
│       │   ├── pricing.txt
│       │   ├── products.txt
│       │   ├── qualification_rules.txt
│       │   └── leads.json             # Sample file; not loaded by the app
│       ├── static/
│       │   ├── index.html
│       │   └── css/style.css
│       ├── tests/
│       │   └── test_lead_qualifier.py
│       ├── requirements.txt
│       ├── requirements_sales.txt
│       ├── SALES_LEAD_README.md
│       ├── run.py
│       └── utils/                  # Empty utility folder
└── .env                            # Root-level local environment configuration
```