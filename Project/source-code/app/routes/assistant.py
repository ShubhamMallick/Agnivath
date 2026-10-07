"""Knowledge-base conversation endpoint."""
from typing import List, Literal
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.routes.leads import lead_qualifier, lead_store

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class ConversationTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: List[ConversationTurn] = Field(default_factory=list)


@router.post("/chat")
async def chat(request: ChatRequest):
    """Answer questions using sales knowledge vectors and processed leads."""
    if not lead_qualifier.vector_store:
        raise HTTPException(status_code=503, detail="Knowledge base is not available")

    try:
        knowledge_entries = {}

        if lead_qualifier.vector_store:
            stored_documents = lead_qualifier.vector_store.get(
                include=["documents", "metadatas"]
            )
            for content, metadata in zip(
                stored_documents.get("documents") or [],
                stored_documents.get("metadatas") or [],
            ):
                if content:
                    source = (metadata or {}).get("source", "Knowledge base")
                    source_name = source.split("/")[-1].split("\\")[-1]
                    label = f"Lead knowledge base / {source_name}"
                    knowledge_entries[(label, content)] = content

        if not knowledge_entries:
            raise HTTPException(status_code=404, detail="No relevant knowledge-base information was found")

        context = "\n\n".join(
            f"Source: {source}\n{content}"
            for source, content in knowledge_entries
        )
        processed_leads = []
        for lead in lead_store.list_leads():
            extracted_info = lead.get("extracted_info") or {}
            processed_leads.append({
                "lead_id": lead.get("lead_id"),
                "created_at": lead.get("created_at"),
                "extracted_info": {
                    key: value for key, value in extracted_info.items()
                    if key not in {"email", "phone"}
                },
                "qualification": lead.get("qualification", {}),
                "notification_sent": lead.get("notification_sent", False),
            })
        processed_context = json.dumps(processed_leads, ensure_ascii=False, indent=2)
        conversation = "\n".join(
            f"{turn.role}: {turn.content}" for turn in request.history[-8:]
        )
        prompt = f"""You are a helpful assistant. The vector context contains all documents from the sales lead knowledge base. The processed-lead context contains leads stored in the local database. Use both sources when relevant. If there are no processed leads, the list will be empty. Use the conversation history to understand follow-up questions. Reply in the language of the user's latest question when supported by the model; when drafting lead outreach, prefer that lead's detected language. If the supplied context does not contain the answer, say so clearly and do not invent details.

    For questions asking for all information, an overview, or everything you know, provide a comprehensive, organized summary covering every source and all relevant processed-lead data present in the supplied context. Do not limit the answer to one source or topic when other sources contain information. Name the source sections in the answer. For a specific question, focus on the relevant details. Do not claim that no other details are available when they appear elsewhere in the supplied context.

Sales knowledge-base vector context:
{context}

Processed-lead context:
{processed_context}

Recent conversation:
{conversation or "No earlier messages."}

User question:
{request.question}

Answer clearly in plain text, using headings and bullets when useful."""

        result = lead_qualifier.llm.invoke(prompt)
        answer = result.content if hasattr(result, "content") else str(result)
        sources = sorted({
            source for source, _ in knowledge_entries
        })
        if processed_leads:
            sources.append("Processed leads")
        return {"answer": answer.strip(), "sources": sources}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not generate an answer: {exc}") from exc