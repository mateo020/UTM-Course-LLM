# search.py
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json
from typing import List, Dict, Any, Tuple
import sys


from v1.src.search.hybrid_search import hybrid_search

router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[5]
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"

# ---------- helpers ----------
import re

COURSE_CODE_RE = re.compile(r"^[A-Z]{3}\s*\d{3}[A-Z]?\d?[HFYS]?$", re.I)

def exact_course_lookup(query: str) -> list[dict[str, Any]]:
    """
    If `query` is a course code, scan courses.json and return the first match
    where the code is found *anywhere* in the `title` field.
    Returns [] when no match or when query doesn’t look like a code.
    """
    if not COURSE_CODE_RE.match(query.strip()):
        return []

    with open(DOCUMENTS_DIR / "courses.json", encoding="utf-8") as f:
        courses = json.load(f)

    q_norm = query.upper().replace(" ", "")
    for course in courses:
        title_norm = course["title"].upper().replace(" ", "")
        if q_norm in title_norm:
            return [course]          # wrap in list so endpoint shape stays the same
    return []


def get_course_info_by_id(hits: List[Tuple[int, float]]) -> List[Dict[str, Any]]:
    """
    Convert (id, score) pairs returned by hybrid_search into
    the structured payload your client expects.
    """
    # Load once per request; cache at module level if perf is a concern
    with open(DOCUMENTS_DIR / "courses.json", encoding="utf-8") as f:
        courses = {c["title"]: c for c in json.load(f)}

    results = []
    for cid, score in hits:
        course = courses.get(cid)
        if course is None:
            continue                 # id in items.json but not in courses.json
        # Adjust / trim fields as you like
        results.append(
            {
                "course_code": course["course_code"],
                "title":        course["title"],
                "description":  course["description"],
                "prerequisites": course.get("prerequisites"),
                "score":        round(score, 4),
            }
        )
    return results

# ---------- endpoint ----------
@router.get("/search")
async def search_courses(query: str = Query(..., min_length=1)):
    try:
        query = query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

  
        exact_hit = exact_course_lookup(query)
        if exact_hit:
            return {"results": exact_hit}


        hits = hybrid_search(query)           # List[(id, score)]
        response = get_course_info_by_id(hits)
        return {"results": response}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")
