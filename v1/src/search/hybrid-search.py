
# init the aiplatform package
from google.cloud import aiplatform
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    HybridQuery,
)
import json
from pathlib import Path
from vertexai.preview.language_models import TextEmbeddingModel
import pandas as pd
from inputData import get_dense_embedding, get_sparse_embedding
PROJECT_ID = "hybrid-search"
LOCATION = "us-central1"

UID = datetime.now().strftime("%m%d%H%M")
BUCKET_NAME = f"hybrid-search-vs-hybridsearch-05240037"
BUCKET_URI = f"gs://hybrid-search-vs-hybridsearch-05240037"
aiplatform.init(project=PROJECT_ID, location=LOCATION)
ROOT_DIR = Path(__file__).resolve().parents[3]

DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"
data_path = str(DOCUMENTS_DIR / "courses.json") 

with open (data_path, "r") as course_data:
    json_data = json.load(course_data)

my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name=f"vs-hybridsearch-index-endpoint-{UID}", public_endpoint_enabled=True
)
my_hybrid_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name=f"vs-hybridsearch-index-{UID}",
    contents_delta_uri=BUCKET_URI,
    dimensions=768,
    approximate_neighbors_count=10,
)

DEPLOYED_HYBRID_INDEX_ID = f"vs_hybridsearch_deployed_{UID}"
my_index_endpoint.deploy_index(
    index=my_hybrid_index, deployed_index_id=DEPLOYED_HYBRID_INDEX_ID
)
query_text = "Kids"
query_dense_emb = get_dense_embedding(query_text)
query_sparse_emb = get_sparse_embedding(query_text)
query = HybridQuery(
    dense_embedding=query_dense_emb,
    sparse_embedding_dimensions=query_sparse_emb["dimensions"],
    sparse_embedding_values=query_sparse_emb["values"],
    rrf_ranking_alpha=0.5,
)

response = my_index_endpoint.find_neighbors(
    deployed_index_id=DEPLOYED_HYBRID_INDEX_ID,
    queries=[query],
    num_neighbors=10,
)

# print results
for idx, neighbor in enumerate(response[0]):
    print(idx,neighbor)