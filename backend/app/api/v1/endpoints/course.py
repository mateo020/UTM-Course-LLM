from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Dict, Any

router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[5]
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"

try:
    with open(DOCUMENTS_DIR / "courses.json", "r", encoding="utf-8") as f:
        _COURSES = json.load(f)
        COURSES_BY_CODE: Dict[str, Dict[str, Any]] = {c["course_code"]: c for c in _COURSES}
        COURSES_BY_TITLE: Dict[str, Dict[str, Any]] = {c["title"]: c for c in _COURSES}
except Exception as e:
    print("[course] Failed to load courses.json:", e)
    COURSES_BY_CODE = {}
    COURSES_BY_TITLE = {}


@router.get("/course/{course_id}")
def get_course_details(course_id: str):
    """Return full course details for a given course code OR title."""
    course = COURSES_BY_CODE.get(course_id) or COURSES_BY_TITLE.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    return course 