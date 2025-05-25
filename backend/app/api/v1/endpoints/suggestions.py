# v1/src/api/suggestions.py
from fastapi import APIRouter, Query, HTTPException
from typing import List
from pathlib import Path
import json
from v1.src.search.autocomplete import autocomplete

router = APIRouter()

@router.get("/suggestions", response_model=List[str])
def get_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="User input"),
    k: int = Query(10, ge=1, le=10, description="Max number of suggestions")
):
    """
    Return up to *k* autocomplete suggestions that start with the prefix *q*.
    """
    try:
        suggestions = autocomplete(q)[:k]   
        print(f"Query: {q}, Suggestions: {suggestions}")  # Debug print
        return suggestions
    except Exception as e:
        print(f"Error in suggestions endpoint: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))
