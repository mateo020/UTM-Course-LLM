import tiktoken
import networkx as nx
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import ollama
import tiktoken
from tqdm import tqdm # import the function
import subprocess
from graspologic.partition import hierarchical_leiden
import asyncio
import openai
from collections import defaultdict
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import json
from networkx.readwrite import json_graph
from langchain_core.documents import Document

client = openai.AsyncOpenAI()  # Optionally: api_key="YOUR_API_KEY"

subprocess.run(["ollama", "pull", "nomic-embed-text"])

import matplotlib.pyplot as plt
ROOT_DIR = Path(__file__).resolve().parents[4]
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"

COMMUNITY_SUMMARIZATION_PROMPT = '''
You are an AI assistant that helps a human analyst to generate a natural language summary of the provided information based on the provided nodes and relationships that belong to the same graph community,

# Goal
Write a short summary of a community, given a list of entities that belong to the community as well as their relationships. The report will be used to inform decision-makers about information associated with the community and their potential impact. The input community information data is present in the below format:
{
'communityId': 'Community id',
 'nodes': [{'id': 'Node id', 'description': 'Brief descrption of node'},
  {'id': 'Node id', 'description': 'Brief descrption of node'},
   ...
  ],
 'relationships': [{'start': 'Node id',
    'description': 'Relationship present between start and end nodes',
    'end': 'Node id'},
  {'start': 'Node id',
    'description': 'Relationship present between start and end nodes',
    'end': 'Node id'}
    ]
}
#########################################################
Generate a comprehensive summary of the community information given below.

{community_info}

Summary:
'''

def generate_graph(prereq_json_path: str):
    with open(prereq_json_path, "r") as f:
        prerequisites = json.load(f)
    # Create a dictionary to store course descriptions
    with open(DOCUMENTS_DIR / "courses.json", encoding="utf-8") as f:
        courses = {c["title"]: c for c in json.load(f)}
    # print(courses)    
    # print(courses.get("CSC148H5"))
    G = nx.Graph()
    # print(courses)
    for node in prerequisites["nodes"]:
       
        
        course = courses.get(node["id"])
        if course is None:
            # print(f"Warning: Course {node['id']} not found in courses.json")
            description = ""
            pq = ""
        else:
            print(f" Course {node['id']}  found in courses.json")
            description = course.get("description", "")
            pq = course.get("prerequisites", "")
        G.add_node(node["id"], description=description, prerequisites=pq)

    for edge in prerequisites["links"]:
        G.add_edge(edge["source"], edge["target"], relationship='prerequisite of')

   
    return G


def creating_embeddings(G):
    # Create embeddings for each node
    lst = []
    nodes_label_mapping_lst = []
    for node in tqdm(G.nodes(data=True)):
        entity = "\nName: " + node[0] + " \nDescription: " + node[1]['description'] + " \nPrerequisites: " + node[1]['prerequisites']
        embed = ollama.embeddings(model="nomic-embed-text", prompt=entity)['embedding']
        lst.append(embed)
        nodes_label_mapping_lst.append(node[0])
    # print(len(lst), len(nodes_label_mapping_lst))
    return lst, nodes_label_mapping_lst

# creating prompt for community summarization
def community_summary_prompt_generator(cluster_id, cluster_nodes):
    cluster_info = {
      "communityId": cluster_id,
      "nodes": [],
      "relationships": []
    }

    for node in cluster_nodes:
      node_data = G.nodes[node]
      node_info = {
        "id": node,
        "description": node_data["description"]
      }
      cluster_info["nodes"].append(node_info)

    for node1, node2, data in G.edges(data=True):
      if node1 in cluster_nodes and node2 in cluster_nodes:
        relationship_info = {
          "start": node1,
          "description": data["relationship"],
          "end": node2
        }
        cluster_info["relationships"].append(relationship_info)

    return cluster_info


async def create_hierarchical_clustering(G):
    communities = hierarchical_leiden(G, max_cluster_size=10)

    # generating community summaries
    node_cluster_dct = defaultdict(list)
    for community in communities:
        node_cluster_dct[community.node].append((community.cluster, community.level))

    cluster_node_dct = defaultdict(list)
    for community in communities:
        cluster_node_dct[community.cluster].append(community.node)

    community_summary = {}
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    for key, val in tqdm(cluster_node_dct.items()):
        prompt = COMMUNITY_SUMMARIZATION_PROMPT.replace("{community_info}", 
                                                        str(community_summary_prompt_generator(key, val)))
        if len(encoding.encode(prompt))>10000:
            prompt = " ".join(prompt.split()[:10000])
            # print(f"prompt truncated for Cluster_{key}")
        
        summary = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
        community_summary[key] = summary.choices[0].message.content

    # storing all community summaries at different heirarchial level for each node
    for node, data in tqdm(G.nodes(data=True)):
        if node in node_cluster_dct.keys():
            node_level_summary = []
            for level in sorted(list(set([x[1] for x in node_cluster_dct[node]]))):
                associated_communities = [y for y in node_cluster_dct[node] if y[1]==level]
                associated_communities_summaries = [community_summary[y[0]] for y in associated_communities]
                node_level_summary.append(("\n".join(associated_communities_summaries), level))
            data["community_summaries"] = [y[0] for y in sorted(node_level_summary, key = lambda x:x[1], reverse=True)]
        else:
            data["community_summaries"] = " "


def store_embeddings(G):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # store node embeddings in vector database
    docs = []
    for node, data in tqdm(G.nodes(data=True)):
        entity = "\nName: " + node + " \nDescription: " + data['description'] + " \nPrerequisites: " + data['prerequisites']
        doc = Document(
        page_content=entity,
        metadata={"source": node}
        )
        docs.append(doc)

    embedding_function = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma.from_documents(docs, embedding_function)

    # save Knowledge graph created in json
    with open("graph.json", "w") as f:
        json.dump(json_graph.node_link_data(G), f)



if __name__ == "__main__":

    G = generate_graph(DOCUMENTS_DIR / "prereq_graph.json")
    lst, nodes_label_mapping_lst = creating_embeddings(G)
    # print(lst)
    # print(nodes_label_mapping_lst)
    asyncio.run(create_hierarchical_clustering(G))
    # Print community summaries for each node
    print("\nCommunity Summaries:")
    for node, data in G.nodes(data=True):
        print(f"\nNode: {node}")
        if isinstance(data['community_summaries'], list):
            print("Hierarchical summaries:")
            for i, summary in enumerate(data['community_summaries'], 1):
                print(f"\nLevel {i}:")
                print(summary)
        else:
            print("No community summaries available")

           # load knowledge graph
    store_embeddings(G)
    G = nx.Graph()
    with open("graph.json", "r") as f:
        G_data = json.load(f)
        G = json_graph.node_link_graph(G_data)