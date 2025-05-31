import asyncio
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import openai
import ollama
import networkx as nx
import json
from networkx.readwrite import json_graph
client = openai.AsyncOpenAI()  # Optionally: api_key="YOUR_API_KEY"

embedding_function = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory="path/to/chroma_db", embedding_function=embedding_function)

# load knowledge graph
G = nx.Graph()
with open("graph.json", "r") as f:
    G_data = json.load(f)
    G = json_graph.node_link_graph(G_data)

PREDICTION_PROMPT = '''
You are an helpful Question Answering AI assistant based on the relevant context provided.
In the context, you are provide informations of some text chunks. Along with that you are also provided information about nodes, relationships and community summaries of the nodes extracted from a relevant portion of knowledge graph according to the question asked. The information is provided in the below format:
CHUNK TEXT: Text chunks provided 
\n\nNODES : Information about nodes having "id" and "node description" 
\n\nRELATIONSHIPS : Relationpships between the nodes contating "start" and "end" node along with their relationship as "description" 
\n\nCUMMUNITY SUMMARIES: Community summaries of the nodes in a list.

#########################################################
Answer the question based on the above context provided and predict the most relevant answer.

Context: {context}

Question: {question}

Answer:
'''
async def main():
    query = '''Write a summary of scope 1 and scope 3 emission related to target Baseline Year, target end/horizon year,
percentage reduction. Give output in a json format.'''
    topk_nodes=12
    topk_chunks = 12
    topk_internal_rel = 12
    topk_external_rel = 12
    nodes = db.similarity_search(query,topk_nodes)

    # getting associated text chunks
    chunks = []
    query_embed = ollama.embeddings(model="nomic-embed-text", prompt=query)['embedding']
    for node in nodes:
        chunks.extend(G.nodes[node.metadata["source"]]['chunks'])

    chunks = list(set(chunks))
    chunks_selected = chunks
    len(chunks_selected)

    # getting top k internal and external relationships 
    within_relationships = []
    between_relationships = []
    nodes_info = []
    nodes_set = set([x.metadata["source"] for x in nodes])

    for node1, node2, data in G.edges(data=True):
        relationship_info = {
            "start": node1,
            "end": node2,
            "description": data["relationship"],
            "score": data["score"]
        }
        if node1 in nodes_set and node2 in nodes_set:
            within_relationships.append(relationship_info)
        elif (node1 in nodes_set and node2 not in nodes_set) or (node2 in nodes_set and node1 not in nodes_set):
            between_relationships.append(relationship_info)

    within_relationships = sorted(within_relationships, key=lambda x: x["score"], reverse=True)[:topk_internal_rel]
    between_relationships = sorted(between_relationships, key=lambda x: x["score"], reverse=True)[:topk_external_rel]

    all_nodes = set()
    relationships = within_relationships + between_relationships

    for rel in relationships:
        all_nodes.add(rel["start"])
        all_nodes.add(rel["end"])

    for node in all_nodes:
        if node in G.nodes:
            node_data = G.nodes[node]
            node_info = {
                "id": node,
                "description": node_data["description"]
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