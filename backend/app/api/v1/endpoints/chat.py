from typing import List, Optional
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
from v1.src.DSPY.rag_dspy import RAGRetriever
from v1.src.DSPY.multi_hop import MultiHop

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

# Initialize RAG retriever
retriever = setup_rag([
    str(DOCUMENTS_DIR / "course_data.txt"),
    str(DOCUMENTS_DIR / "program_info.txt")
])
set_rag_retriever(retriever)
print("RAG retriever initialized with both course data and program info")
# print(retriever)
# print(get_relevant_context("test"))
# print("="*80)

# llm = ChatOpenAI(
#     api_key=OPENAI_API_KEY,
#     model="gpt-4",
#     temperature=0,
#     streaming=False,
# import dspy



llm = dspy.LM('gpt-4o-mini', api_key=os.getenv("OPENAI_API_KEY"))

dspy.configure(lm=llm)

# class InMemoryHistory(BaseChatMessageHistory, BaseModel):
#     """In memory implementation of chat message history."""

#     messages: List[BaseMessage] = Field(default_factory=list)

#     def add_messages(self, messages: List[BaseMessage]) -> None:
#         """Add a list of messages to the store"""
#         self.messages.extend(messages)

#     def clear(self) -> None:
#         self.messages = []

store = {}

# def get_session_history(
#     user_id: str, conversation_id: str
# ) -> BaseChatMessageHistory:
#     if (user_id, conversation_id) not in store:
#         store[(user_id, conversation_id)] = InMemoryHistory()
#     return store[(user_id, conversation_id)]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You're an assistant who's good at {ability}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])
   
prompt_template = """
You are an academic assistant. Answer based on the context.
If the context is not relevant, state that clearly. Don't answer with anything other than what is in the context.

Context:
{context}

Question:
{question}

Answer:
"""



prompt = ChatPromptTemplate.from_template(prompt_template)
rag_chain = prompt | llm | StrOutputParser()



# with_message_history = RunnableWithMessageHistory(
#     rag_chain,
#     get_session_history=get_session_history,
#     input_messages_key="question",
#     history_messages_key="history",
#     history_factory_config=[
#         ConfigurableFieldSpec(
#             id="user_id",
#             annotation=str,
#             name="User ID",
#             description="Unique identifier for the user.",
#             default="",
#             is_shared=True,
#         ),
#         ConfigurableFieldSpec(
#             id="conversation_id",
#             annotation=str,
#             name="Conversation ID",
#             description="Unique identifier for the conversation.",
#             default="",
#             is_shared=True,
#         ),
#     ],
# )

class ChatRequest(BaseModel):
    question: str
    chatHistory: Optional[List[str]] = None
    session_id: Optional[str] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Question is required.")

        session_id = request.session_id or str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        rag_retriever = get_rag_retriever()
        dspy_retriever = RAGRetriever(rag_retriever)
        multi_hop = MultiHop(dspy_retriever)

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

