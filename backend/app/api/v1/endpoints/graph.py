# app/api/v1/endpoints/graph.py

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Set, Optional
router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[5]
GRAPH_PATH = ROOT_DIR / "v1" / "files" / "prereq_graph.json"

# Load once at startup so you’re not hitting disk on every call
with open(GRAPH_PATH, "r") as f:
    full_graph = json.load(f)


# Build a quick reverse-adjacency dict: course → list of its direct prereqs
rev_adj: dict[str, list[str]] = {}
for link in full_graph["links"]:
    rev_adj.setdefault(link["target"], []).append(link["source"])


@router.get("/prereq-graph-advanced/{course_id}")
def get_subgraph(course_id: str):
    def find_ancestors(course_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        if visited is None:
            visited = set()
        for parent in rev_adj.get(course_id, []):
            if parent not in visited:
                visited.add(parent)
                find_ancestors(parent, visited)
        return visited
    #N = number of courses = number of nodes = len(full_graph["nodes"])
    #L = number of prereq relationships = number of links = len(full_graph["links"])

    # Find all ancestors leading up to this course in O(N + L)
    ancestor_ids = find_ancestors(course_id)

    # Full list of links for filtering
    all_links = full_graph["links"]

    # Collect only the links among ancestors (plus those pointing to course_id)
    related_links = [
        l for l in all_links
        if (l["source"] in ancestor_ids and l["target"] in ancestor_ids)
        or (l["source"] in ancestor_ids and l["target"] == course_id)
    ]

    # Immediate forward links out of this course
    forward_links = [
        l for l in all_links
        if l["source"] == course_id
    ]

    combined_links = related_links + forward_links

    # Build the set of node IDs we need
    node_ids = {
        course_id,
        *[l["source"] for l in combined_links],
        *[l["target"]   for l in combined_links]
    }

    # Filter nodes down to just those in our subgraph
    nodes = [n for n in full_graph["nodes"] if n["id"] in node_ids]

    return {"nodes": nodes, "links": combined_links}


@router.get("/prereq-graph/{course_id}")
def get_subgraph(course_id: str):
    links = [l for l in full_graph["links"] if l["source"] == course_id or l["target"] == course_id]
    node_ids = {course_id, *[l["source"] for l in links], *[l["target"] for l in links]}
    nodes    = [n for n in full_graph["nodes"] if n["id"] in node_ids]
    # print(node_ids)
    # print(links)
    return {"nodes": nodes, "links": links}
