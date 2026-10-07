# AI Usage Documentation

## 1. Overview

This project is an **AI-Powered Sales Lead Qualification Assistant** designed to help sales teams process and prioritize leads received through a company's website.

The system uses AI to:

- Extract structured information from incoming leads.
- Identify business requirements and buying signals.
- Qualify and prioritize leads.
- Retrieve relevant sales knowledge using RAG.
- Recommend the next action for the salesperson.
- Answer sales-related questions through a dashboard assistant.

AI tools were used throughout the development process as development partners for business analysis, architecture design, coding, debugging, testing, and refinement.

---

## 2. AI Tools and Technologies Used

| Tool / Technology | Purpose |
|---|---|
| **ChatGPT** | Business analysis, architecture design, prompt engineering, debugging, and solution refinement |
| **Devin** | Repository-level development, debugging, implementation, and testing |
| **VS Code GitHub Copilot** | Code completion, implementation assistance, refactoring, and debugging |
| **Groq – GPT-OSS-20B** | Runtime lead extraction, qualification assistance, recommendations, and dashboard Q&A |
| **LangChain** | LLM orchestration, prompt management, document processing, and retrieval |
| **ChromaDB** | Vector storage and semantic retrieval of sales knowledge |
| **FastAPI** | Backend API and application framework |

---

# 3. Important AI Usage

## 3.1 ChatGPT – Business Problem Analysis and Architecture

### AI Tool

**ChatGPT**

### Purpose

ChatGPT was used to understand the business problem and design a focused AI-first solution instead of attempting to build a complete CRM system.

### Important Prompt

> Design a focused AI-first Sales Lead Qualification Assistant for a company receiving leads from its website. The system should use LangChain, an LLM, a vector database, lead qualification, sales recommendations, and multilingual support. Recommend what information should be extracted from each lead and how the system should process it.

### How It Helped

ChatGPT helped break the broad business problem into a focused prototype consisting of:

1. Lead ingestion.
2. Structured information extraction.
3. Lead qualification and scoring.
4. RAG-based sales knowledge retrieval.
5. Sales recommendations.
6. Sales dashboard and conversational assistant.

This helped keep the project appropriately scoped for the assessment.

---

# 4. ChatGPT – Debugging and Solution Refinement

### AI Tool

**ChatGPT**

### Purpose

ChatGPT was used to analyze implementation errors and improve the robustness of the AI pipeline.

### Important Prompt

> The lead qualification system is returning a validation error because `product_interest` is `None` while the Pydantic model expects a string. Analyze the problem and recommend a robust approach for optional information in LLM-generated structured output.

### How It Helped

The issue was identified as a mismatch between LLM-generated optional values and the Pydantic schema.

The solution was to allow legitimately missing lead information to be represented as nullable values instead of forcing the model to invent information.

This improved the reliability of structured lead extraction.

---

# 5. Devin – Repository Development and Debugging

### AI Tool

**Devin**

### Purpose

Devin was used as a development agent for repository-level implementation, debugging, code inspection, and testing.

### Important Prompt

> Inspect the complete lead qualification pipeline and determine why a lead with a specific business requirement, large company, senior decision-maker, demo request, and two-month timeline is being classified as Low Priority. Trace the scoring logic, identify the root cause, implement an explainable scoring mechanism, and test both high-intent and low-intent leads.

### How It Helped

Devin helped inspect the project across multiple files and trace the problem through the qualification and scoring pipeline.

The qualification logic was refined so that strong buying signals such as:

- Specific business requirements.
- Company fit.
- Senior decision-maker.
- Demo request.
- Defined implementation timeline.

could contribute appropriately to the final lead score.

The scoring process was also made more explainable so that sales users can understand why a lead received a particular priority.

---

# 6. VS Code GitHub Copilot – Implementation Assistance

### AI Tool

**GitHub Copilot in VS Code**

### Purpose

GitHub Copilot was used during implementation for code completion, repetitive code generation, refactoring, and debugging assistance.

### Important Prompt

> Implement the FastAPI endpoint for receiving a website lead and pass the validated lead data into the qualification service. Return the qualification score, priority, reasons, missing information, and recommended next action.

### How It Helped

Copilot accelerated implementation of backend components and repetitive application code.

The generated code was reviewed, modified, and integrated into the existing application based on the project's architecture and requirements.

---

# 7. Groq – Runtime Lead Information Extraction

### AI Tool

**Groq – GPT-OSS-20B**

### Framework

**LangChain**

### Purpose

The runtime LLM is used to extract structured business information from unstructured website lead messages.

### Important Prompt

> Extract structured information from the following sales lead. Identify company size, industry, product interest, use case, pain points, budget signals, implementation timeline, purchase intent, urgency, requirements, and missing information. Do not invent information that is not present in the lead.

### How It Helped

The LLM converts an unstructured lead message into structured information that can be passed to the qualification and scoring pipeline.

For example, a lead such as:

> We are looking for an AI solution for around 500 employees. We want to automate internal document search and customer support. We would like a demo and need deployment within 2 months.

can be transformed into structured business information such as:

- Company size: Approximately 500 employees.
- Use case: Internal document search and customer support.
- Timeline: 2 months.
- Intent: Strong purchase intent.
- Engagement: Demo requested.
- Missing information: Budget.

---

# 8. LangChain + ChromaDB – RAG-Based Sales Knowledge

### Technologies

- **LangChain**
- **ChromaDB**
- **LLM**

### Purpose

The system uses RAG to retrieve relevant information from the company's sales knowledge base.

The knowledge base contains information such as:

- Products.
- Pricing.
- FAQs.
- Qualification rules.

### Important Prompt

> Using the extracted lead information and retrieved sales knowledge, evaluate the lead's business fit, requirements, intent, timeline, and engagement. Provide qualification reasons, relevant product information, missing information, and a recommended next action. Do not invent missing information.

### How It Helped

The vector database allows the system to retrieve relevant business information before generating qualification and recommendations.

This makes the AI response more grounded in the available company knowledge instead of relying only on the model's general knowledge.

---

# 9. AI-Assisted Sales Recommendation

### AI Tool

**Groq – GPT-OSS-20B**

### Purpose

Generate a practical next action for the salesperson after qualification.

### Prompt

> Based on the qualified lead and available sales knowledge, recommend the most appropriate next action for the salesperson. Explain why the action is appropriate and identify any important information that should be collected before contacting the lead.

### How It Helped

The system can recommend actions such as:

- Schedule a product demo.
- Contact the lead.
- Request missing information.
- Follow up with pricing information.
- Place the lead into a nurture workflow.

The recommendation is intended to assist the salesperson rather than replace the salesperson's final decision.

---

# 10. Limitations and Responsible AI Use

The project is a prototype and has several limitations.

- The system provides recommendations and does not make final sales decisions.
- LLM-generated information may contain errors and should be reviewed when necessary.
- Missing information should be identified rather than invented.
- Lead records are currently held in application memory and may be lost when the application restarts.
- Production CRM integration is not implemented.
- Production access control and deployment hardening are future improvements.
- External LLM providers process the information required for AI processing.
- Multilingual behavior depends on the selected language and configured model capabilities.
- API keys and credentials are stored using environment variables and are not included in the submission.

---

# 11. Development Approach

AI tools were used as **development partners rather than as unattended code generators**.

The development process involved:

1. Understanding the business requirement.
2. Designing the system architecture.
3. Using AI tools to explore implementation approaches.
4. Generating and modifying code.
5. Testing the implementation.
6. Debugging errors.
7. Reviewing AI-generated solutions.
8. Refining the system based on observed behavior.
9. Testing different lead scenarios.
10. Documenting limitations and future improvements.

The final implementation was reviewed and integrated according to the project's requirements and architecture.

---

# 12. Summary

AI was used at both the **development stage** and the **runtime stage**.

### Development-time AI

- ChatGPT
- Devin
- GitHub Copilot

### Runtime AI

- Groq – GPT-OSS-20B
- LangChain
- ChromaDB-based RAG

The combination allowed the project to use AI for both **building the solution** and **delivering the core business functionality** of automated sales lead qualification.