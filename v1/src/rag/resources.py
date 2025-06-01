from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import openai
import ollama
import networkx as nx
import json
from pathlib import Path
from networkx.readwrite import json_graph

ROOT_DIR = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = ROOT_DIR / "files"

def load_embeddings(persist_dir="chroma_db"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(embedding_function=embeddings, persist_directory=str(persist_dir))  # <-- convert to str
    print(f"[INFO] Vector DB loaded from {persist_dir}")
    return db

# load knowledge graph
def load_graph():
    G = nx.Graph()
    with open(DOCUMENTS_DIR / "graph.json", "r") as f:
        G_data = json.load(f)
    G = json_graph.node_link_graph(G_data)
    return G