"""
Lead Qualification System
Scores and qualifies leads based on extracted information and knowledge base
"""
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


class QualificationResult(BaseModel):
    """Result of lead qualification"""
    lead_id: str
    priority: str = Field(description="HIGH, MEDIUM, or LOW")
    score: int = Field(description="Score from 0-100")
    reasons: List[str] = Field(description="Reasons for the priority score")
    recommended_product: Optional[str] = Field(description="Recommended product based on interest")
    relevant_info: str = Field(description="Relevant product/industry information from knowledge base")
    missing_info: List[str] = Field(description="Critical missing information")
    next_action: str = Field(description="Recommended next action for sales team")


class LeadQualifier:
    """Qualifies leads using RAG with knowledge base"""
    
    def __init__(self, provider="groq"):
        self.provider = provider
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL")
        )
        
        # Initialize LLM
        if provider == "groq":
            self.llm = ChatOpenAI(
                openai_api_key=os.getenv("GROQ_API_KEY"),
                openai_api_base="https://api.groq.com/openai/v1",
                model_name="openai/gpt-oss-20b",
                temperature=0
            )
        else:
            self.llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
                model_name=os.getenv("OPENROUTER_MODEL"),
                temperature=0
            )
        
        self.vector_store = None
        self.qa_chain = None
        
        # Load knowledge base
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base documents into vector store"""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            documents = []
            
            # Load all text files from knowledge base
            for file_path in data_dir.glob("*.txt"):
                loader = TextLoader(str(file_path))
                documents.extend(loader.load())
            
            if documents:
                # Split documents
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = text_splitter.split_documents(documents)
                
                # Create vector store
                chroma_dir = Path(__file__).parent.parent.parent / "lead_chroma_db"
                self.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=str(chroma_dir)
                )
                self.vector_store.persist()
                
                # Create QA chain
                self.create_qa_chain()
                print("Knowledge base loaded successfully")
            else:
                print("No knowledge base documents found")
                
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
    
    def create_qa_chain(self):
        """Create RAG chain for qualification"""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        prompt_template = """You are a sales lead qualification expert. Use the following context from our knowledge base to qualify the lead.

Context: {context}

Lead Information:
- Name: {name}
- Company: {company}
- Job Title: {job_title}
- Company Size: {company_size}
- Industry: {industry}
- Product Interest: {product_interest}
- Use Case: {use_case}
- Pain Points: {pain_points}
- Budget: {budget}
- Timeline: {timeline}
- Purchase Intent: {purchase_intent}
- Action Requested: {action_requested}
- Missing Info: {missing_info}

Based on the qualification rules in the context and the lead information:

1. Determine priority (HIGH, MEDIUM, LOW):
   - HIGH: Clear purchase intent, specific requirement, large org, budget available, specific timeline, demo requested, decision-maker
   - MEDIUM: Clear business problem, fits target customer, researching, unclear timeline/budget
   - LOW: Browsing only, no clear requirement, general info only, no use case

2. Calculate a score (0-100) based on the strength of buying signals

3. List 3-5 reasons for this priority

4. Recommend the most suitable product based on their interest and profile

5. Provide relevant information from the knowledge base about their industry/product

6. List critical missing information

7. Recommend the next action for the sales team

Format your response as a JSON object with these exact fields:
{{
  "priority": "HIGH/MEDIUM/LOW",
  "score": 0-100,
  "reasons": ["reason1", "reason2", ...],
  "recommended_product": "product name",
  "relevant_info": "relevant knowledge base information",
  "missing_info": ["missing1", "missing2", ...],
  "next_action": "recommended action"
}}

Return only valid JSON, no additional text."""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "name", "company", "job_title", "company_size", 
                           "industry", "product_interest", "use_case", "pain_points",
                           "budget", "timeline", "purchase_intent", "action_requested", "missing_info"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def qualify_lead(self, lead_info: dict, lead_id: str) -> QualificationResult:
        """Qualify a lead based on extracted information"""

        if not self.vector_store:
            return self.fallback_qualification(lead_info, lead_id)

        try:
            import json

            lead_query = (
                f"Name: {lead_info.get('name', 'Unknown')}\n"
                f"Company: {lead_info.get('company', 'Unknown')}\n"
                f"Job Title: {lead_info.get('job_title', 'Unknown')}\n"
                f"Company Size: {lead_info.get('company_size', 'Unknown')}\n"
                f"Industry: {lead_info.get('industry', 'Unknown')}\n"
                f"Product Interest: {lead_info.get('product_interest', 'Unknown')}\n"
                f"Use Case: {lead_info.get('use_case', 'Unknown')}\n"
                f"Pain Points: {lead_info.get('pain_points', 'Unknown')}\n"
                f"Budget: {lead_info.get('budget', 'Unknown')}\n"
                f"Timeline: {lead_info.get('timeline', 'Unknown')}\n"
                f"Purchase Intent: {lead_info.get('purchase_intent', 'Unknown')}\n"
                f"Action Requested: {lead_info.get('action_requested', 'Unknown')}\n"
                f"Missing Info: {', '.join(lead_info.get('missing_info', []) or ['None'])}"
            )

            relevant_docs = self.vector_store.similarity_search(lead_query, k=5)
            context = "\n\n".join(doc.page_content for doc in relevant_docs)

            prompt = f"""You are a sales lead qualification expert. Use the following context from our knowledge base to qualify the lead.

Context: {context}

Lead Information:
{lead_query}

Based on the qualification rules in the context and the lead information:

1. Determine priority (HIGH, MEDIUM, LOW):
   - HIGH: Clear purchase intent, specific requirement, large org, budget available, specific timeline, demo requested, decision-maker
   - MEDIUM: Clear business problem, fits target customer, researching, unclear timeline/budget
   - LOW: Browsing only, no clear requirement, general info only, no use case

2. Calculate a score (0-100) based on the strength of buying signals

3. List 3-5 reasons for this priority

4. Recommend the most suitable product based on their interest and profile

5. Provide relevant information from the knowledge base about their industry/product

6. List critical missing information

7. Recommend the next action for the sales team

Format your response as a JSON object with these exact fields:
{{
  "priority": "HIGH/MEDIUM/LOW",
  "score": 0-100,
  "reasons": ["reason1", "reason2", ...],
  "recommended_product": "product name",
  "relevant_info": "relevant knowledge base information",
  "missing_info": ["missing1", "missing2", ...],
  "next_action": "recommended action"
}}

Return only valid JSON, no additional text."""

            result = self.llm.invoke(prompt)
            content = result.content.strip() if hasattr(result, "content") else str(result).strip()
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            qual_data = json.loads(content)
            score = max(0, min(100, int(qual_data.get("score", 50))))

            return QualificationResult(
                lead_id=lead_id,
                priority=qual_data.get("priority", "MEDIUM"),
                score=score,
                reasons=qual_data.get("reasons", []),
                recommended_product=qual_data.get("recommended_product"),
                relevant_info=qual_data.get("relevant_info", ""),
                missing_info=qual_data.get("missing_info") or lead_info.get("missing_info", []),
                next_action=qual_data.get("next_action", "Review lead manually")
            )

        except Exception as e:
            print(f"Error qualifying lead: {e}")
            return self.fallback_qualification(lead_info, lead_id)
    
    def fallback_qualification(self, lead_info: dict, lead_id: str) -> QualificationResult:
        """Simple rule-based qualification as fallback"""
        
        score = 50
        reasons = []
        priority = "MEDIUM"
        
        # Simple scoring rules
        job_title = str(lead_info.get("job_title") or "").lower()
        company_size = str(lead_info.get("company_size") or "").lower()
        budget = str(lead_info.get("budget") or "").lower()
        timeline = str(lead_info.get("timeline") or "").lower()
        action = str(lead_info.get("action_requested") or "").lower()
        
        # Job title scoring
        if any(role in job_title for role in ["cto", "cio", "ceo", "vp", "head", "director"]):
            score += 15
            reasons.append("Senior decision-maker role")
        
        # Company size scoring
        if any(size in company_size for size in ["enterprise", "large", "1000", "2000", "3000"]):
            score += 15
            reasons.append("Large organization")
        elif any(size in company_size for size in ["medium", "100", "200", "300", "500"]):
            score += 10
            reasons.append("Medium-sized organization")
        
        # Budget scoring
        if any(b in budget for b in ["approved", "available", "budget"]):
            score += 20
            reasons.append("Budget available or approved")
        
        # Timeline scoring
        if any(t in timeline for t in ["immediate", "month", "quarter", "30 days", "60 days"]):
            score += 15
            reasons.append("Specific implementation timeline")
        
        # Action scoring
        if any(a in action for a in ["demo", "call", "discussion"]):
            score += 15
            reasons.append("Requested demo or call")
        
        # Determine priority
        if score >= 70:
            priority = "HIGH"
        elif score >= 40:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        score = max(0, min(100, score))

        return QualificationResult(
            lead_id=lead_id,
            priority=priority,
            score=score,
            reasons=reasons,
            recommended_product=lead_info.get("product_interest"),
            relevant_info="Knowledge base not available",
            missing_info=lead_info.get("missing_info", []),
            next_action="Review lead manually"
        )
