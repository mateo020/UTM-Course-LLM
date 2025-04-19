import json
import re
from pathlib import Path

# Load your JSON file
with open(Path("v1/files/courses.json"), "r") as f:
    courses = json.load(f)

# Initialize nodes and edges
nodes = set()
edges = []

# Utility function to extract course codes from the prerequisites string
def extract_course_codes(prereq_str):
    if not prereq_str:
        return []
    # Match patterns like CSC108H5, MAT257Y5, etc.
    return re.findall(r"[A-Z]{3}[0-9]{3}[HY][0-9]", prereq_str)

# Build graph
for course in courses:
    course_title = course["title"]  # e.g., "MAT337H5"
    prereq_str = course.get("prerequisites", "")

    nodes.add(course_title)

    prereqs = extract_course_codes(prereq_str)
    for prereq in prereqs:
        edges.append({"source": prereq, "target": course_title})
        nodes.add(prereq)

# Format as node-link structure (D3-style or for visualization)
graph = {
    "nodes": [{"id": node} for node in sorted(nodes)],
    "links": edges
}

# Optional: write to JSON
with open("prereq_graph.json", "w") as f:
    json.dump(graph, f, indent=2)

print("Graph built with", len(nodes), "nodes and", len(edges), "edges.")
