# Sales Lead Qualification Assistant

This application is an AI-powered sales qualification prototype that helps a sales team process website leads more efficiently. It ingests incoming lead data, extracts business details using an LLM, qualifies the lead using a knowledge base and vector search, and exposes the result through a web dashboard.

## Project structure

```text
Project/source-code/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       ├── __init__.py
│       └── leads.py
├── core/
│   ├── __init__.py
│   ├── lead_processor.py
│   ├── lead_qualifier.py
│   ├── notifier.py
│   └── rag.py
├── data/
│   ├── faq.txt
│   ├── pricing.txt
│   ├── products.txt
│   ├── qualification_rules.txt
│   └── leads.json
├── static/
│   ├── css/style.css
│   └── index.html
├── utils/
├── requirements.txt
├── requirements_sales.txt
├── SALES_LEAD_README.md
├── run.py
└── __init__.py
```

## Main components

### 1. Lead processor
File: `core/lead_processor.py`

This module uses an LLM to transform a raw lead message into structured fields, including:

- company size
- industry
- product interest
- use case
- pain points
- budget
- timeline
- purchase intent
- action requested
- missing info

The extraction is designed to work with a lead message and other available metadata like company and role.

### 2. Lead qualifier
File: `core/lead_qualifier.py`

This module uses a vector store built from the knowledge base files in `data/` and classifies the lead using RAG-style retrieval. It determines:

- priority: HIGH / MEDIUM / LOW
- score: 0-100
- reasons
- recommended product
- relevant information
- missing information
- next action

### 3. Notification layer
File: `core/notifier.py`

This stores notifications for qualified leads and is designed to model an internal sales alert system.

### 4. API layer
File: `app/routes/leads.py`

This exposes the lead management API:

- `POST /api/leads/ingest`
- `POST /api/leads/qualify`
- `GET /api/leads/list`
- `GET /api/leads/{lead_id}`
- `POST /api/leads/batch-upload`

### 5. Dashboard
File: `static/index.html`

The dashboard allows a sales team to:

- add a lead manually
- select LLM provider
- view statistics
- filter leads by priority
- inspect extracted details and recommended actions

## Business workflow

1. A website lead is submitted from a contact form, demo request, pricing request, or downloadable resource
2. The system extracts structured lead data from the message
3. The lead is scored based on buying signals and product fit
4. Sales gets a prioritized view of leads
5. High-priority leads are flagged for immediate response

## Prototype status

This project is a functioning prototype and is appropriate for demonstration, validation, and prototyping work. It is not yet a full production CRM or enterprise sales platform.

## Environment

The app expects environment variables such as:

```env
OPENROUTER_API_KEY=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=...
GROQ_API_KEY=...
```

## Run locally

```bash
cd Project/source-code
python run.py
```

Open in browser:

```text
http://localhost:8080
```

## Data sources used

The actual knowledge base is in:

- `data/products.txt`
- `data/qualification_rules.txt`
- `data/faq.txt`
- `data/pricing.txt`

These are the product and sales decision inputs for qualification.

## Future enhancements

- save leads in a database
- integrate email/Slack/CRM systems
- support full lead assignment workflows
- add authentication and role-based access
- improve analytics and reporting
- deploy as a production web app
