# pip install bm25s
import bm25s
from bm25s.hf import BM25HF
import numpy as np

from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import json
from typing import List, Dict, Any
import os
import sys
router = APIRouter()

root_dir = Path(__file__).resolve().parents[5]
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / 'v1'))
sys.path.append(str(root_dir / 'v1' / 'src'))
router = APIRouter()

#absolute paths 
ROOT_DIR = Path(__file__).resolve().parents[5] 
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"



# Initialize RAG retriever


def load_course_data():
    try:
        data_path = str(DOCUMENTS_DIR / "course_data.txt")
        with open(data_path, 'r', encoding='utf-8') as f:
            corpus = f.readlines()
            retriever = bm25s.BM25(corpus=corpus)
            retriever.index(bm25s.tokenize(corpus))
            # retriever.save("bm25s_very_big_index", corpus=corpus)
            return retriever

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading course data: {str(e)}")

# Initialize BM25 with course data
retriever = load_course_data()
# print(corpus)

def parse_results(results, scores):
    parsed_results = []
   
    for i in range(results.shape[1]):
        doc, score = results[0, i], scores[0, i]
        doc = str(doc) 
        # print(f"Rank {i+1} (score: {score:.2f}): {doc}")
        if score > 2.5:
            if "Course:" in doc:
                result = doc.split("Course:")[1]
                course_code = result.split("•")[0].strip()     
                parsed_results.append(course_code) 
    return parsed_results

def get_course_info(results):
    course_info = []
    for result in results:
        try:
            with open(DOCUMENTS_DIR / "courses.json", "r") as f:
                courses = json.load(f)
                
            
            print(results)
            for course in courses:
                if course["title"] == result:
                    course_info.append({
                        "course_code": course["course_code"],
                        "title": course["title"],
                        "description": course["description"],
                        "prerequisites": course["prerequisites"]
                    })
                    break
                    
            return course_info
                    
        except Exception as e:
            print(f"Error getting course info: {str(e)}")
            return []

        


@router.post("/search")
async def search_courses(query: Dict[str, str]):
    try:
        search_query = query.get("query", "").strip()
        if not search_query:
            return {"results": []}

        # Get top 10 most relevant results
        results, scores = retriever.retrieve(bm25s.tokenize(search_query), k=10)
        
        parsed_results = parse_results(results, scores)
        course_info = get_course_info(parsed_results)
        print(course_info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
