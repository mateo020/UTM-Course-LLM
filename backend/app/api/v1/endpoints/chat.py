from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.schema.output_parser import StrOutputParser

load_dotenv()
# Add v1
root_dir = Path(__file__).resolve().parents[5]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'v1'))
sys.path.append(str(root_dir / 'v1' / 'src'))
router = APIRouter()

#absolute paths 
BACKEND_DIR = Path(__file__).resolve().prents[3] 
DOCUMENTS_DIR = BACKEND_DIR / "files"


from v1.src.rag.retriever import setup_rag, set_rag_retriever, get_relevant_context

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# 

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4",
    temperature=0,
    streaming=False,
)

prompt_template = """
You are an academic assistant. Answer based on the context.
If the context is not relevant, state that clearly Dont asnwer with anithing other than the what is in the context.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
rag_chain = prompt | llm | StrOutputParser()

class ChatRequest(BaseModel):
    question: str
    chatHistory: Optional[List[str]] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required.")

        
        

        response = rag_chain.invoke({
            "context": context_text,
            "question": request.question
        })

        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
