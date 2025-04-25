# app/api/v1/endpoints/graph.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[5]
GRAPH_PATH = ROOT_DIR / "v1" / "files" / "prereq_graph.json"

# Load once at startup so you’re not hitting disk on every call
with open(GRAPH_PATH, "r") as f:
    full_graph = json.load(f)

# Build a quick adjacency map for O(1) look‑ups


@router.get("/prereq-graph/{course_id}")
def get_subgraph(course_id: str):
    links = [l for l in full_graph["links"] if l["source"] == course_id or l["target"] == course_id]
    node_ids = {course_id, *[l["source"] for l in links], *[l["target"] for l in links]}
    nodes    = [n for n in full_graph["nodes"] if n["id"] in node_ids]
    # print(node_ids)
    # print(links)
    return {"nodes": nodes, "links": links}


