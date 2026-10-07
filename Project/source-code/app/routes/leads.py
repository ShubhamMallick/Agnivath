"""
Lead Management Routes
API endpoints for lead ingestion, qualification, and retrieval
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.lead_processor import LeadProcessor
from core.lead_qualifier import LeadQualifier
from core.notifier import Notifier
import json

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Initialize components
lead_processor = LeadProcessor(provider="groq")
lead_qualifier = LeadQualifier(provider="groq")
notifier = Notifier()

# In-memory storage for demo (use database in production)
leads_db = []


class LeadIngest(BaseModel):
    """Model for lead ingestion"""
    lead_id: str
    name: str
    email: str
    phone: Optional[str] = None
    company: str
    job_title: str
    message: str
    source: str
    language: str = "English"
    provider: str = "groq"  # Add provider selection


class LeadResponse(BaseModel):
    """Model for lead response"""
    lead_id: str
    extracted_info: dict
    qualification: dict
    notification_sent: bool


@router.post("/ingest")
async def ingest_lead(lead: LeadIngest):
    """
    Ingest a new lead from website/webhook
    Automatically extracts info, qualifies, and sends notification
    """
    try:
        # Convert to dict
        lead_data = lead.dict()
        
        # Initialize processors with selected provider
        processor = LeadProcessor(provider=lead.provider)
        qualifier = LeadQualifier(provider=lead.provider)
        
        # Extract structured information
        lead_info = processor.extract_lead_info(lead_data)
        extracted_data = lead_info.dict()
        
        # Qualify the lead
        qualification = qualifier.qualify_lead(extracted_data, lead.lead_id)
        qual_data = qualification.dict()
        
        # Send notification if priority is MEDIUM or HIGH
        notification_sent = False
        if qual_data["priority"] in ["HIGH", "MEDIUM"]:
            notifier.send_notification(qual_data, lead_data)
            notification_sent = True
        
        # Store lead
        lead_record = {
            "lead_id": lead.lead_id,
            "original_data": lead_data,
            "extracted_info": extracted_data,
            "qualification": qual_data,
            "notification_sent": notification_sent,
            "created_at": datetime.utcnow().isoformat()
        }
        leads_db.append(lead_record)
        
        return {
            "status": "success",
            "lead_id": lead.lead_id,
            "provider_used": lead.provider,
            "extracted_info": extracted_data,
            "qualification": qual_data,
            "notification_sent": notification_sent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qualify")
async def qualify_lead(lead: LeadIngest):
    """
    Qualify a lead without storing it
    Useful for preview/testing
    """
    try:
        lead_data = lead.dict()
        
        # Initialize processors with selected provider
        processor = LeadProcessor(provider=lead.provider)
        qualifier = LeadQualifier(provider=lead.provider)
        
        # Extract structured information
        lead_info = processor.extract_lead_info(lead_data)
        extracted_data = lead_info.dict()
        
        # Qualify the lead
        qualification = qualifier.qualify_lead(extracted_data, lead.lead_id)
        
        return {
            "status": "success",
            "lead_id": lead.lead_id,
            "provider_used": lead.provider,
            "extracted_info": extracted_data,
            "qualification": qualification.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_leads(priority: Optional[str] = None):
    """
    List all leads with optional priority filter
    """
    if priority:
        filtered = [lead for lead in leads_db if lead["qualification"]["priority"] == priority]
        return {"leads": filtered, "count": len(filtered)}
    
    return {"leads": leads_db, "count": len(leads_db)}


@router.get("/statistics")
async def lead_statistics():
    """Summarize sample leads and leads processed in the current session."""
    sample_data_path = Path(__file__).resolve().parents[3] / "sample_data" / "leads.json"
    sample_leads = []
    if sample_data_path.exists():
        with sample_data_path.open("r", encoding="utf-8") as sample_file:
            sample_leads = json.load(sample_file)

    leads_by_id = {}
    for index, lead in enumerate(sample_leads):
        lead_id = str(lead.get("lead_id") or f"sample-{index}")
        leads_by_id[lead_id] = {
            "source": lead.get("source") or "Unknown",
            "qualification": lead.get("qualification"),
        }

    for lead in leads_db:
        original_data = lead.get("original_data") or {}
        lead_id = str(lead.get("lead_id") or f"session-{len(leads_by_id)}")
        leads_by_id[lead_id] = {
            "source": original_data.get("source") or "Unknown",
            "qualification": lead.get("qualification"),
        }

    priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNSCORED": 0}
    score_ranges = {"0-39": 0, "40-69": 0, "70-100": 0, "Unscored": 0}
    source_counts = {}

    for lead in leads_by_id.values():
        source = lead["source"]
        source_counts[source] = source_counts.get(source, 0) + 1
        qualification = lead.get("qualification") or {}
        priority = str(qualification.get("priority") or "").upper()
        if priority in priority_counts and priority != "UNSCORED":
            priority_counts[priority] += 1
        else:
            priority_counts["UNSCORED"] += 1

        score = qualification.get("score")
        if score is None:
            score_ranges["Unscored"] += 1
        else:
            try:
                score = float(score)
            except (TypeError, ValueError):
                score_ranges["Unscored"] += 1
                continue

            if score < 40:
                score_ranges["0-39"] += 1
            elif score < 70:
                score_ranges["40-69"] += 1
            else:
                score_ranges["70-100"] += 1

    return {
        "total": len(leads_by_id),
        "sample_leads": len(sample_leads),
        "session_leads": len(leads_db),
        "priority_counts": priority_counts,
        "score_ranges": [
            {"label": label, "count": count}
            for label, count in score_ranges.items()
        ],
        "source_counts": source_counts,
    }


@router.get("/{lead_id}")
async def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    for lead in leads_db:
        if lead["lead_id"] == lead_id:
            return lead
    
    raise HTTPException(status_code=404, detail="Lead not found")


@router.post("/batch-upload")
async def batch_upload(leads: List[LeadIngest]):
    """
    Upload multiple leads at once (e.g., from CSV file)
    """
    results = []
    
    for lead in leads:
        try:
            result = await ingest_lead(lead)
            results.append(result)
        except Exception as e:
            results.append({
                "lead_id": lead.lead_id,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total": len(leads),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len([r for r in results if r.get("status") == "error"]),
        "results": results
    }
