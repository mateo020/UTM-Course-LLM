import json 
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys
import os

# Add the parent directory to sys.path to allow absolute imports
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from search.trie import Trie

# Get the absolute path to the v1 directory
V1_DIR = Path(__file__).resolve().parents[3] / "v1"
DOCUMENTS_DIR = V1_DIR / "files"

def load_course_json() -> List[Dict[str, Any]]:
    """Load course data from the JSON file."""
    data_path = str(DOCUMENTS_DIR / "courses.json")
    print(f"Loading course data from: {data_path}")
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
            print(f"Successfully loaded {len(data)} courses")
            return data
    except Exception as e:
        print(f"Error loading course data: {str(e)}")
        return []

# Build list of entries and mapping
course_data = load_course_json()
entry_map: Dict[str, str] = {}
entries: List[str] = []
for course in course_data:
    code = course.get('course_code', '')
    title = course.get('title', '')
    if code:
        entries.append(code.lower())
        entry_map[code.lower()] = code
    if title:
        entries.append(title.lower())
        entry_map[title.lower()] = title

print(f"Prepared {len(entries)} entries for Trie (codes + titles)")

# Initialize Trie
_trie = None

def get_trie() -> Trie:
    global _trie
    if _trie is None:
        print("Initializing Trie with course codes and titles")
        _trie = Trie()
        _trie.formTrie(entries)
        print("Trie initialization complete")
    return _trie

def autocomplete(prefix: str) -> List[str]:
    prefix_lower = prefix.lower()
    trie = get_trie()
    results_lower = trie.autocomplete(prefix_lower)
    results_original: List[str] = [entry_map[r] for r in results_lower]
    return results_original

