"""
Lead Information Extraction using LLM
Extracts structured information from lead messages
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import os
import json

load_dotenv()


class LeadInfo(BaseModel):
    """Structured lead information extracted from message"""
    name: str = Field(description="Contact person's name")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number if provided")
    company: str = Field(description="Company name")
    job_title: str = Field(description="Job title or role")
    company_size: Optional[str] = Field(description="Number of employees or company size")
    industry: Optional[str] = Field(description="Industry sector")
    product_interest: Optional[str] = Field(description="Which product or solution they're interested in")
    use_case: Optional[str] = Field(description="Specific use case or problem they want to solve")
    pain_points: Optional[str] = Field(description="Pain points or challenges mentioned")
    budget: Optional[str] = Field(description="Budget information or budget signals")
    timeline: Optional[str] = Field(description="Implementation timeline or urgency")
    purchase_intent: Optional[str] = Field(description="Level of purchase intent")
    action_requested: Optional[str] = Field(description="Specific action requested (demo, call, info)")
    language: str = Field(description="Language of the message")
    missing_info: list[str] = Field(description="List of important information that could not be extracted")


class LeadProcessor:
    """Processes lead messages to extract structured information"""
    
    def __init__(self, provider="groq"):
        self.provider = provider

        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is missing from the environment.")
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base="https://api.groq.com/openai/v1",
                model_name="openai/gpt-oss-20b",
                temperature=0
            )
        else:
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = os.getenv("OPENROUTER_BASE_URL")
            model = os.getenv("OPENROUTER_MODEL")
            if not api_key or not base_url or not model:
                raise ValueError("OPENROUTER configuration is incomplete. Check OPENROUTER_API_KEY, OPENROUTER_BASE_URL, and OPENROUTER_MODEL.")
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base=base_url,
                model_name=model,
                temperature=0
            )
    
    def extract_lead_info(self, lead_data: dict) -> LeadInfo:
        """Extract structured information from lead data"""

        message = str(lead_data.get("message") or "")
        name = str(lead_data.get("name") or "")
        email = str(lead_data.get("email") or "")
        phone = str(lead_data.get("phone") or "")
        company = str(lead_data.get("company") or "")
        job_title = str(lead_data.get("job_title") or "")
        source = str(lead_data.get("source") or "")
        language = str(lead_data.get("language") or "English")
        
        prompt = PromptTemplate(
            template="""You are a sales lead information extraction expert. Extract structured information from the following lead data.

Lead Data:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Company: {company}
- Job Title: {job_title}
- Message: {message}
- Source: {source}
- Language: {language}

Extract the following information from the message and available data:
1. company_size - Number of employees or company size (small, medium, large, startup, enterprise, etc.)
2. industry - Industry sector (healthcare, finance, retail, technology, education, etc.)
3. product_interest - Which product or solution they're interested in (Enterprise AI Platform, AI Customer Support, AI Document Processing, AI Chatbot, etc.)
4. use_case - Specific use case or problem they want to solve
5. pain_points - Pain points or challenges mentioned
6. budget - Budget information or budget signals (available, approved, discussing, unclear, etc.)
7. timeline - Implementation timeline or urgency (immediate, 1 month, 2 months, this quarter, next quarter, unclear, etc.)
8. purchase_intent - Level of purchase intent (high, medium, low, evaluating, browsing, etc.)
9. action_requested - Specific action requested (demo, call, information, pricing, technical discussion, etc.)
10. missing_info - List of important information that could not be extracted (e.g., budget, timeline, company size)

If information is not available in the message or provided data, mark it as null or empty.
For missing_info, list what important business information is missing for sales qualification.

IMPORTANT: Return ONLY a valid JSON object. No markdown, no code blocks, no additional text. The response must start with {{ and end with }}.

Return the result as a JSON object with these exact fields: company_size, industry, product_interest, use_case, pain_points, budget, timeline, purchase_intent, action_requested, missing_info.

Extract only from the provided data. Do not invent or hallucinate information.""",
            input_variables=["name", "email", "phone", "company", "job_title", "message", "source", "language"]
        )
        
        try:
            result = self.llm.invoke(prompt.format(
                name=name,
                email=email,
                phone=phone,
                company=company,
                job_title=job_title,
                message=message,
                source=source,
                language=language
            ))
            
            # Clean the response - remove markdown code blocks if present
            content = result.content.strip()
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            # Parse the LLM response
            extracted_data = json.loads(content)
            
            # Create LeadInfo object
            lead_info = LeadInfo(
                name=name,
                email=email,
                phone=phone or None,
                company=company,
                job_title=job_title,
                company_size=extracted_data.get("company_size") or None,
                industry=extracted_data.get("industry") or None,
                product_interest=extracted_data.get("product_interest") or None,
                use_case=extracted_data.get("use_case") or None,
                pain_points=extracted_data.get("pain_points") or None,
                budget=extracted_data.get("budget") or None,
                timeline=extracted_data.get("timeline") or None,
                purchase_intent=extracted_data.get("purchase_intent") or None,
                action_requested=extracted_data.get("action_requested") or None,
                language=language,
                missing_info=extracted_data.get("missing_info") or []
            )
            
            return lead_info
            
        except Exception as e:
            print(f"Error extracting lead info: {e}")
            print(f"LLM response was: {result.content if 'result' in locals() else 'N/A'}")
            # Return basic info if extraction fails
            return LeadInfo(
                name=name,
                email=email,
                phone=phone,
                company=company,
                job_title=job_title,
                company_size=None,
                industry=None,
                product_interest=None,
                use_case=None,
                pain_points=None,
                budget=None,
                timeline=None,
                purchase_intent=None,
                action_requested=None,
                language=language,
                missing_info=["Extraction failed - using fallback"]
            )
