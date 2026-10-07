from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL")
        )
        
        # OpenRouter LLM
        self.openrouter_llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
            model_name=os.getenv("OPENROUTER_MODEL")
        )
        
        # Groq LLM
        self.groq_llm = ChatOpenAI(
            openai_api_key=os.getenv("GROQ_API_KEY"),
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="openai/gpt-oss-20b"
        )
        
        self.current_llm = self.openrouter_llm  # Default
        self.vector_store = None
        self.qa_chain = None

    def load_document(self, file_path):
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError("Unsupported file type. Use PDF or DOCX.")
        documents = loader.load()
        return documents

    def split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(documents)

    def create_vector_store(self, documents, persist_directory="../chroma_db"):
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        self.vector_store.persist()

    def create_qa_chain(self):
        retriever = self.vector_store.as_retriever()
        
        # Custom prompt template for structured responses
        prompt_template = """You are a helpful assistant that provides well-structured, formatted answers based on the given context.

Context: {context}

Question: {question}

Instructions for your answer:
1. Use proper formatting with bullet points, numbered lists, or tables where appropriate
2. Organize information into clear sections with headers
3. Use bold or emphasis for key terms
4. Make the response easy to read and scan
5. If the information doesn't exist in the context, state that clearly

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.current_llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def set_provider(self, provider):
        if provider == "groq":
            self.current_llm = self.groq_llm
        else:
            self.current_llm = self.openrouter_llm
        
        # Recreate chain with new LLM
        if self.vector_store:
            self.create_qa_chain()

    def query(self, question, provider="openrouter"):
        if not self.qa_chain:
            return "Please load documents first"
        
        # Switch provider if different
        if provider != ("groq" if self.current_llm == self.groq_llm else "openrouter"):
            self.set_provider(provider)
        
        result = self.qa_chain.invoke({"query": question})
        return result["result"]
