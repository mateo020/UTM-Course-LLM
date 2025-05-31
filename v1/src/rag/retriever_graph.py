import asyncio
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import openai
import ollama
import networkx as nx
import json
from pathlib import Path
from networkx.readwrite import json_graph
from langchain_core.documents import Document
from tqdm import tqdm

client = openai.AsyncOpenAI()  # Optionally: api_key="YOUR_API_KEY"

embedding_function = OllamaEmbeddings(model="nomic-embed-text")



ROOT_DIR = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = ROOT_DIR / "files"


def load_embeddings(persist_dir="chroma_db"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(embedding_function=embeddings, persist_directory=str(persist_dir))  # <-- convert to str
    print(f"[INFO] Vector DB loaded from {persist_dir}")
    return db

# load knowledge graph
G = nx.Graph()
with open(DOCUMENTS_DIR / "graph.json", "r") as f:
    G_data = json.load(f)
    G = json_graph.node_link_graph(G_data)



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
async def main():
    query = 'Give me courses that cover the topic of machine learning?'
    db = load_embeddings()
    topk_nodes=12
    topk_chunks = 12
    topk_internal_rel = 12
    topk_external_rel = 12
    nodes = db.similarity_search(query,topk_nodes)
    # print("nodes ------")
    # print(nodes)
    # getting associated text chunks
    chunks = []
   
    query_embed = ollama.embeddings(model="nomic-embed-text", prompt=query)['embedding']
    for node in nodes:
        # print("node ------")
        # print(node.metadata["source"])
        chunks.extend(G.nodes[node.metadata["source"]])
       

    chunks = list(set(chunks))
    chunks_selected = chunks
    len(chunks_selected)
    # print("chunks_selected ------")
    # print(chunks_selected)

    # getting top k internal and external relationships 
    relationships = []
    
    nodes_info = []
    nodes_set = set([x.metadata["source"] for x in nodes])

    for node1, node2, data in G.edges(data=True):
        # print("data ------")
        # print(data)
        relationship_info = {
            "start": node1,
            "end": node2,
            "description": data["relationship"],
            
        }
        if node1 in nodes_set and node2 in nodes_set:
            relationships.append(relationship_info)
        

    all_nodes = set()
    
    for rel in relationships:
        all_nodes.add(rel["start"])
        all_nodes.add(rel["end"])

    for node in all_nodes:
        if node in G.nodes:
            node_data = G.nodes[node]
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

    # getting immediate summaries
    summaries_selected = []
    for node in nodes:
        summaries_selected.append(G.nodes[node.metadata["source"]]['community_summaries'][0])

    len(summaries_selected)

    # generating prompt
    context = "CHUNK TEXT: \n" + "\n".join(chunks_selected) + \
            "\n\nNODES: \n" + str(relationships_selected["nodes"]) + \
            "\n\nRELATIONSHIPS: \n" + str(relationships_selected["relationships"]) + \
            "\n\nCUMMUNITY SUMMARIES: \n" + str(summaries_selected)

    prompt = PREDICTION_PROMPT.replace("{question}", query)
    prompt = prompt.replace("{context}", context)
    print(context)
    # generating response
    answer = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                seed=42
            )
    print(answer.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(main())