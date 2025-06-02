from typing import Dict, List
import asyncio
from pathlib import Path
import json
import networkx as nx
from networkx.readwrite import json_graph
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import re

COURSE_RE = re.compile(r'\b[A-Z]{3}\s*\d{3}[A-Z]?\b') 
from langchain_core.documents import Document
PREDICTION_PROMPT = '''
You are an helpful Question Answering AI assistant based on the relevant context provided.
In the context, you are provide informations of some text chunks. Along with that you are also provided information about nodes, relationships and community summaries of the nodes extracted from a relevant portion of knowledge graph according to the question asked. The information is provided in the below format:
CHUNK TEXT: Text chunks provided 
\n\nNODES : Information about nodes having "id" and "node description" and "prerequisites" 
\n\nRELATIONSHIPS : Relationpships between the nodes contating "start" and "end". Start node is a prerequisite of End node.
\n\nCUMMUNITY SUMMARIES: Community summaries of the nodes in a list, similar courses.

#########################################################
Answer the question based on the above context provided and predict the most relevant answer.

Context: {context}

Question: {question}

Answer:
'''


ROOT_DIR = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = ROOT_DIR / "files"




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

# load knowledge graph
G = nx.Graph()
with open(DOCUMENTS_DIR / "graph.json", "r") as f:
    G_data = json.load(f)
    G = json_graph.node_link_graph(G_data)
class GraphRetriever:
    """
    Async callable that returns {'passages': List[str]}.
    Suitable for DSPy MultiHop.
    """
    def __init__(self, k: int = 12):
        self.db, self.G, self.k = load_embeddings(), G, k

    
    def _extract_course_codes(self, query: str) -> set[str]:
        """Pull explicit course codes out of the query."""
        # normalise to “CSC384” instead of “CSC 384”
        return {re.sub(r'\s+', '', m) for m in COURSE_RE.findall(query.upper())}

    def _fetch_docs_by_code(self, code: str, n_chunks: int = 3) -> List[Document]:
        """Grab a few chunks whose metadata["source"] == code."""
        explicit_codes = self._extract_course_codes(code)
        return explicit_codes
        # Chroma v0.4+: db.get(where=…) returns matching docs + embeddings
        # print("-----------code---------------------")
        # print(code)
        # print("--------------------------------")
        # out = self.db.get(
        #     where={'source': "code"},
        #     include=['documents'],
        #     limit=n_chunks
        # )
        # return [
        #     Document(page_content=text, metadata={'source': code})
        #     for text in out['documents']
        # ]

    def __call__(self, query: str) -> Dict[str, List[str]]:
        # 1) semantic search
        passages: List[str] = []
        docs: List[Document] = self.db.similarity_search(query, self.k)
        explicit_codes = self._extract_course_codes(query)
        for code in explicit_codes:
            explicit_docs: List[Document] = self.db.similarity_search(code, 5)
            node_set_explicit = {d.metadata["source"] for d in explicit_docs}   
            for code in node_set_explicit:
                data = self.G.nodes[code]
                desc  = data.get("description", "")
            
                prereq = data.get("prerequisites", "")
                community_summaries = data.get("community_summaries", "")
                passages.append(f"{code}: {desc}  Prereqs: {prereq} Community Summaries: {community_summaries}")    
            print(node_set_explicit)
       
         
    
        # 2) build enriched passages
        
        node_set = {d.metadata["source"] for d in docs}
        print(node_set)

        for code in node_set:
            data = self.G.nodes[code]
            desc  = data.get("description", "")
           
            prereq = data.get("prerequisites", "")
            community_summaries = data.get("community_summaries", "")
            passages.append(f"{code}: {desc}  Prereqs: {prereq} Community Summaries: {community_summaries}")



        relationships = []
        
        nodes_info = []
        
        for node1, node2, data in self.G.edges(data=True):
            relationship_info = {
                "start": node1,
                "end": node2,
                "description": data["relationship"],
                
            }
            if node1 in node_set and node2 in node_set:
                relationships.append(relationship_info)
            

        all_nodes = set()
        
        for rel in relationships:
            all_nodes.add(rel["start"])
            all_nodes.add(rel["end"])

        for node in all_nodes:
            if node in self.G.nodes:
                node_data = self.G.nodes[node]
                node_info = {
                    "id": node,
                    "description": node_data["description"],
                    "prerequisites": node_data["prerequisites"]
                }
                nodes_info.append(node_info)

        relationships_selected = {
            "nodes": nodes_info,
            "relationships": relationships
        }

        passages.append(str(relationships_selected))
        return {"passages": passages}







  
    # prompt = PREDICTION_PROMPT.replace("{question}", query)
    # prompt = prompt.replace("{context}", context)
    # print(context)
    # # generating response
    # answer = await client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             temperature=0.1,
    #             messages=[{"role": "user", "content": prompt}],
    #             stream=False,
    #             seed=42
    #         )
    # print(answer.choices[0].message.content)

# if __name__ == "__main__":
#     # asyncio.run(retriever())