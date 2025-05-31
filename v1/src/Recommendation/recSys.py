import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pickle
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from node2vec import Node2Vec
import sys
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[3]

DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"


def load_course_json() -> List[Dict[str, Any]]:
    data_path = str(DOCUMENTS_DIR / "courses.json") 
    with open(data_path, 'r') as f:
        return json.load(f)

def load_cached_embeddings() -> Dict[str, np.ndarray]:
    data_path = str(DOCUMENTS_DIR / "course_embeddings.json") 
    with open(data_path, 'r') as f:
        return json.load(f)

def parse_prerequisites(prereq_str: str) -> List[Any]:
    if prereq_str.lower() == "none":
        return []

    pattern = r'[A-Z]{3}[0-9]{3}[HY][135]'
    and_parts = [part.strip() for part in re.split(r'\band\b', prereq_str, flags=re.IGNORECASE)]

    result = []
    for part in and_parts:
        codes = re.findall(pattern, part)
        if len(codes) > 1:
            result.append(codes)
        elif len(codes) == 1:
            result.append(codes[0])

    return result

def generate_edges(prereq_str: str, course_title: str) -> List[Tuple[str, str]]:
    parsed_prereqs = parse_prerequisites(prereq_str)
    edges = []
    for prereq in parsed_prereqs:
        if isinstance(prereq, list):
            for or_prereq in prereq:
                edges.append((or_prereq, course_title))
        else:
            edges.append((prereq, course_title))
    return edges

def build_prereq_dict(courses: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, str]]]:
    prereq_dict = {}
    for course in courses:
        code = course['title']
        prereq_str = course.get("prerequisites", "none")
        prereqs = generate_edges(prereq_str, code)
        prereq_dict[code] = prereqs
    return prereq_dict




def load_course_word2vec():
    data_path = DOCUMENTS_DIR / "course_embeddings.json"
    with open(data_path, "r") as f:
        raw = json.load(f)
    course_embeddings = {course: np.array(vec, dtype=np.float32) for course, vec in raw.items()}
    return course_embeddings


def generate_hybrid_embedding_matrix(
    embeddings_dict: Dict[str, np.ndarray],
    course_embeddings: Dict[str, np.ndarray],
    alpha: float = 0.9548
) -> np.ndarray:
    for key in list(course_embeddings.keys()):
        if key not in embeddings_dict:
            course_embeddings.pop(key, None)

    node2vec_matrix = np.array(list(course_embeddings.values()))
    semantic_embeddings = np.array(list(embeddings_dict.values()))


    hybrid_matrix = alpha * semantic_embeddings + (1-alpha) * node2vec_matrix
    return hybrid_matrix

def get_similar_courses(course_id: str, hybrid_embeddings: Dict[str, np.ndarray],
                        hybrid_matrix_normalized: np.ndarray, top_k: int = 9) -> List[Tuple[str, float]]:
    course_idx = list(hybrid_embeddings.keys()).index(course_id)
    course_emb = hybrid_matrix_normalized[course_idx].reshape(1, -1)
    similarities = cosine_similarity(course_emb, hybrid_matrix_normalized)[0]
    sorted_indices = similarities.argsort()[::-1][1:top_k + 1]
    return [(list(hybrid_embeddings.keys())[i], similarities[i]) for i in sorted_indices]

class CourseRecommender:
    def __init__(self,
                 embeddings_file: str = 'course_embeddings.json',
                 courses_file: str = './files/courses.json',
                 dimensions: int = 1536,
                 walk_length: int = 10,
                 num_walks: int = 100,
                 p: float = 1,
                 q: float = 4,
                 alpha: float = 0.9348):
        self.embeddings_file = embeddings_file
        self.courses_file = courses_file
        self.dimensions = dimensions
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.p = p
        self.q = q
        self.alpha = alpha

        self.embeddings_dict = load_cached_embeddings()
        self.courses_json = load_course_json()
        self.prerequisites = build_prereq_dict(self.courses_json)
        self.course_embeddings = load_course_word2vec()
        self.hybrid_matrix = generate_hybrid_embedding_matrix(self.embeddings_dict, self.course_embeddings, self.alpha)
        self.hybrid_matrix_normalized = normalize(self.hybrid_matrix, norm='l2')
        self.hybrid_embeddings = {
            course: self.hybrid_matrix[idx]
            for idx, course in enumerate(self.embeddings_dict.keys())
            if course in self.course_embeddings
        }

    def get_similar_courses(self, course_id: str, top_k: int = 9) -> List[Tuple[str, float]]:
        return get_similar_courses(course_id, self.hybrid_embeddings, self.hybrid_matrix_normalized, top_k)

if __name__ == "__main__":
    recommender = CourseRecommender()
    print(recommender.get_similar_courses("CSC108H5"))
