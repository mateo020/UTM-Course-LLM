import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from node2vec import Node2Vec
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        """Initialize the course recommender system."""
        self.embeddings_file = embeddings_file
        self.courses_file = courses_file
        self.dimensions = dimensions
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.p = p
        self.q = q
        self.alpha = alpha
        
        # Load data
        self.embeddings_dict = self._load_embeddings()
        self.courses_json = self._load_courses()
        
        # Build graph and generate embeddings
        self.prerequisites = self._build_prereq_dict()
        self.G = self._build_graph()
        self.course_embeddings = self._generate_node2vec_embeddings()
        self.hybrid_embeddings = self._create_hybrid_embeddings()
        self.hybrid_matrix_normalized = self._normalize_embeddings()

    def _load_embeddings(self) -> Dict[str, Any]:
        """Load course embeddings from cache file."""
        try:
            with open(self.embeddings_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Embeddings file {self.embeddings_file} not found")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in embeddings file {self.embeddings_file}")
            return {}

    def _load_courses(self) -> List[Dict[str, Any]]:
        """Load course data from JSON file."""
        try:
            with open(self.courses_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Courses file {self.courses_file} not found")
            return []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in courses file {self.courses_file}")
            return []

    def _parse_prerequisites(self, prereq_str: str) -> List[Any]:
        """Parse prerequisite string into list of course codes."""
        if prereq_str.lower() == "none":
            return []

        pattern = r'[A-Z]{3}[0-9]{3}[HY][135]'
        and_parts = [part.strip() for part in re.split(r'\band\b', prereq_str, flags=re.IGNORECASE)]

        result = []
        for part in and_parts:
            codes = re.findall(pattern, part)
            if len(codes) > 1:
                result.append(codes)  # OR condition
            elif len(codes) == 1:
                result.append(codes[0])  # single prerequisite

        return result

    def _generate_edges(self, prereq_str: str, course_title: str) -> List[Tuple[str, str]]:
        """Generate edges from prerequisite string and course title."""
        parsed_prereqs = self._parse_prerequisites(prereq_str)
        edges = []
        for prereq in parsed_prereqs:
            if isinstance(prereq, list):  # OR condition
                for or_prereq in prereq:
                    edges.append((or_prereq, course_title))
            else:  # Single prerequisite (AND)
                edges.append((prereq, course_title))
        return edges

    def _build_prereq_dict(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build dictionary of prerequisites for each course."""
        prereq_dict = {}
        for course in self.courses_json:
            code = course['title']
            prereq_str = course["prerequisites"]
            prereqs = self._generate_edges(prereq_str, code)
            prereq_dict[code] = prereqs
        return prereq_dict

    def _build_graph(self) -> nx.DiGraph:
        """Build directed graph from prerequisites."""
        G = nx.DiGraph()
        for course, prereqs in self.prerequisites.items():
            for prereq in prereqs:
                G.add_edge(prereq[0], prereq[1])
        G.add_nodes_from(self.prerequisites.keys())
        return G

    def _generate_node2vec_embeddings(self) -> Dict[str, np.ndarray]:
        """Generate node2vec embeddings for the graph."""
        node2vec = Node2Vec(
            self.G,
            dimensions=self.dimensions,
            walk_length=self.walk_length,
            num_walks=self.num_walks,
            workers=2,
            p=self.p,
            q=self.q,
            seed=42
        )
        model = node2vec.fit(window=5, min_count=1)
        return {course: model.wv[course] for course in self.G.nodes()}

    def _create_hybrid_embeddings(self) -> Dict[str, np.ndarray]:
        """Create hybrid embeddings combining semantic and structural information."""
        semantic_embeddings = np.array(list(self.embeddings_dict.values()))
        node2vec_matrix = np.array(list(self.course_embeddings.values()))
        
        hybrid_embeddings = (self.alpha * semantic_embeddings + 
                           (1 - self.alpha) * node2vec_matrix)
        
        return {
            course: hybrid_embeddings[idx]
            for idx, course in enumerate(self.embeddings_dict.keys())
        }

    def _normalize_embeddings(self) -> np.ndarray:
        """Normalize hybrid embeddings using L2 normalization."""
        hybrid_matrix = np.array(list(self.hybrid_embeddings.values()))
        return normalize(hybrid_matrix, norm='l2')

    def get_similar_courses(self, course_id: str, top_k: int = 9) -> List[Tuple[str, float]]:
        """Get top k similar courses for a given course."""
        try:
            course_idx = list(self.hybrid_embeddings.keys()).index(course_id)
            course_emb = self.hybrid_matrix_normalized[course_idx].reshape(1, -1)
            
            similarities = cosine_similarity(course_emb, self.hybrid_matrix_normalized)[0]
            sorted_indices = similarities.argsort()[::-1][1:top_k+1]
            
            return [(list(self.hybrid_embeddings.keys())[i], similarities[i]) 
                   for i in sorted_indices]
        except ValueError:
            logger.error(f"Course {course_id} not found in embeddings")
            return []
        except Exception as e:
            logger.error(f"Error getting similar courses: {e}")
            return []

# Initialize global recommender instance
recommender = CourseRecommender()
