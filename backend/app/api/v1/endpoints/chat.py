from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

load_dotenv()

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# Load documents once at startup
loader_course = TextLoader("./app/files/course_data.txt", encoding = 'UTF-8')
loader_program = TextLoader("./app/files/program_info (2).txt", encoding = 'UTF-8')
all_docs = loader_course.load() + loader_program.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=100)
splits = text_splitter.split_documents(all_docs)

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")
vector_store = FAISS.from_documents(splits, embeddings)
retriever = vector_store.as_retriever()

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4",
    temperature=0,
    streaming=False,
)

prompt_template = """
You are an academic assistant. Answer based on the context.
If the context is not relevant, state that clearly.

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

        context_docs = retriever.invoke(request.question)
        context_text = "\n".join(doc.page_content for doc in context_docs)

        response = rag_chain.invoke({
            "context": context_text,
            "question": request.question
        })

        return {"answer": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
