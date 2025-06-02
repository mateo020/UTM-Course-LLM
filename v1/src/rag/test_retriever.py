from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import sys
import uuid
import json
import networkx as nx
from networkx.readwrite import json_graph
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
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

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
ROOT_DIR = Path(__file__).resolve().parents[3]
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"
from v1.src.rag.retriever import setup_rag, set_rag_retriever, get_relevant_context, get_rag_retriever
from v1.src.rag.retriever_graph import GraphRetriever
from v1.src.DSPY.rag_dspy import RAGRetriever
from v1.src.DSPY.multi_hop import MultiHop
from v1.src.rag.resources import load_embeddings, load_graph


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")


# Check if data sources exist
course_data_path = DOCUMENTS_DIR / "course_data.txt"
program_info_path = DOCUMENTS_DIR / "program_info.txt"
courses_path = DOCUMENTS_DIR / "courses.json"

if not course_data_path.exists():
    raise FileNotFoundError(f"Course data file not found at: {course_data_path}")
if not program_info_path.exists():
    raise FileNotFoundError(f"Program info file not found at: {program_info_path}")

# Initialize RAG retriever
retriever_vectorstore = setup_rag([
    str(course_data_path),
    str(program_info_path)
])
set_rag_retriever(retriever_vectorstore)
print("RAG retriever initialized with both course data and program info")

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

def load_embeddings(persist_dir="chroma_db"):
    print("--------------------------------")
    print("load_embeddings")
    print("--------------------------------")
    db_path = Path(persist_dir)
    print(f"Looking for DB at: {db_path.absolute()}")
    print(f"DB exists: {db_path.exists()}")
    
    if db_path.exists():
        files = list(db_path.glob("*"))
        print(f"Files in DB dir: {files}")
    else:
        print(f"DB not found at: {db_path.absolute()}") 
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(embedding_function=embeddings, persist_directory=str(persist_dir))
    
    # Test if DB has any documents
    test_docs = db.similarity_search("test", k=1)
    print(f"DB has {len(test_docs)} documents")
    
    return db

prompt = ChatPromptTemplate.from_template(prompt_template)
rag_chain = prompt | llm | StrOutputParser()

def rag_vectorstore(query):
    rag_retriever = get_rag_retriever()
    dspy_retriever = RAGRetriever(rag_retriever)
    multi_hop = MultiHop(dspy_retriever)

    print(f"[DEBUG] Running multi-hop for question: {query}")
    response = multi_hop(query)
    llm.inspect_history(1)

    return {
        "answer": response.answer,
        "context": response.context,
    }


def graph_rag(query):
    try:
        print("=== CHAT ENDPOINT STARTED ===")
        
       
        print("=== ABOUT TO CREATE RETRIEVER ===")

        
        
        retriever = GraphRetriever(k=12)  # This line calls load_embeddings()
        print("=== RETRIEVER CREATED ===")
        
        print("--------------------------------")
        print("retriever initialized")
        print("--------------------------------")
        multi_hop = MultiHop(retriever=retriever, passages_per_hop=5, max_hops=4)

        
        

        print(f"[DEBUG] Running multi-hop for question: {query}")
        response = multi_hop(query)
        llm.inspect_history(1)

        return {
            "answer": response.answer,
            "context": response.context,
        
        }

    except Exception as e:
        print(f"[ERROR] Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    query = "what are the prerequisites for CSC209?"
    
    graph_rag(query)
    # rag_vectorstore(query)
    # db = load_embeddings()
    # G = nx.Graph()
    # with open(DOCUMENTS_DIR / "graph.json", "r") as f:
    #     G_data = json.load(f)
    #     G = json_graph.node_link_graph(G_data)

    # print(G.nodes["CSC369H5"])
    
        


if __name__ == "__main__":
    main()