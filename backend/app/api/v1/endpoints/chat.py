from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.schema.output_parser import StrOutputParser
from langchain.chains import create_history_aware_retriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)
import dspy
load_dotenv()
# Add v1
root_dir = Path(__file__).resolve().parents[5]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'v1'))
sys.path.append(str(root_dir / 'v1' / 'src'))
router = APIRouter()

#absolute paths 
ROOT_DIR = Path(__file__).resolve().parents[5] 
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"
from v1.src.rag.retriever import setup_rag, set_rag_retriever, get_relevant_context, get_rag_retriever
from v1.src.rag.retriever_graph import GraphRetriever
from v1.src.DSPY.rag_dspy import RAGRetriever
from v1.src.DSPY.multi_hop import MultiHop
from v1.src.rag.resources import load_embeddings, load_graph


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# # Initialize RAG retriever
# retriever = setup_rag([
#     str(DOCUMENTS_DIR / "course_data.txt"),
#     str(DOCUMENTS_DIR / "program_info.txt")
# ])
# set_rag_retriever(retriever)
# print("RAG retriever initialized with both course data and program info")

# db = load_embeddings()
# print(db)
# G = load_graph()
# print("G initialized")



llm = dspy.LM('gpt-4o-mini', api_key=os.getenv("OPENAI_API_KEY"))

dspy.configure(lm=llm)








prompt_template = '''
You are an helpful Question Answering AI assistant based on the relevant context provided.
In the context, you are provide informations of some text chunks. Along with that you are also provided information about nodes, relationships and community summaries of the nodes extracted from a relevant portion of knowledge graph according to the question asked. The information is provided in the below format:

\n\nNODES : Information about nodes having "id" and "node description" and "prerequisites" 
\n\nRELATIONSHIPS : Relationpships between the nodes contating "start" and "end". Start node is a prerequisite of End node.
\n\nCUMMUNITY SUMMARIES: Community summaries of the nodes in a list, similar courses.

#########################################################
Answer the question based on the above context provided and predict the most relevant answer.

Context: {context}

Question: {question}

Answer:
'''



prompt = ChatPromptTemplate.from_template(prompt_template)
rag_chain = prompt | llm | StrOutputParser()





class ChatRequest(BaseModel):
    question: str
    chatHistory: Optional[List[str]] = None
    session_id: Optional[str] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        print("=== CHAT ENDPOINT STARTED ===")
        
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required.")

        print("=== ABOUT TO CREATE RETRIEVER ===")
        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        retriever = GraphRetriever(k=12)  # This line calls load_embeddings()
        print("=== RETRIEVER CREATED ===")
        
        print("--------------------------------")
        print("retriever initialized")
        print("--------------------------------")
        multi_hop = MultiHop(retriever=retriever, passages_per_hop=5, max_hops=4)

        
        

        print(f"[DEBUG] Running multi-hop for question: {request.question}")
        response = multi_hop(request.question)
        llm.inspect_history(1)

        return {
            "answer": response.answer,
            "context": response.context,
            "session_id": session_id
        }

    except Exception as e:
        print(f"[ERROR] Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

