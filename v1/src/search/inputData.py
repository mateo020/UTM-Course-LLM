from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    HybridQuery,
)
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import json
from google.cloud import storage
import sys
from pathlib import Path
from datetime import datetime
from vertexai.preview.language_models import TextEmbeddingModel
UID = datetime.now().strftime("%m%d%H%M")

PROJECT_ID = "hybrid-search"


ROOT_DIR = Path(__file__).resolve().parents[3]

DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"
data_path = str(DOCUMENTS_DIR / "courses.json") 


model = TextEmbeddingModel.from_pretrained("text-embedding-005")


# wrapper
def get_dense_embedding(text):
    return model.get_embeddings([text])[0].values


def create_bucket(bucket_name):
    """Creates a new bucket."""
    # bucket_name = "your-new-bucket-name"

    storage_client = storage.Client()

    bucket = storage_client.create_bucket(bucket_name)

    print(f"Bucket {bucket.name} created")




def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


with open (data_path, "r") as course_data:
    json_data = json.load(course_data)


df = pd.DataFrame(json_data)
df = df[['title','description','course_code']]

# Sample Text Data
titles_only   = df['title'].tolist()
descs_only    = df['description'].tolist()
names_only = df['course_code'].tolist()

# Initialize TfidfVectorizer
vectorizer = TfidfVectorizer()

# Fit and Transform
vectorizer.fit_transform(names_only)


def get_sparse_embedding(text):
    # Transform Text into TF-IDF Sparse Vector
    tfidf_vector = vectorizer.transform([text])

    # Create Sparse Embedding for the New Text
    values = []
    dims = []
    for i, tfidf_value in enumerate(tfidf_vector.data):
        values.append(float(tfidf_value))
        dims.append(int(tfidf_vector.indices[i]))
    return {"values": values, "dimensions": dims}

#create input data file

# create bucket
BUCKET_NAME = f"{PROJECT_ID}-vs-hybridsearch-{UID}"

create_bucket(BUCKET_NAME)




items = []
for i in range(len(df)):
    id = titles_only[i]
    name = names_only[i]
    dense_embedding = get_dense_embedding(name)
    sparse_embedding = get_sparse_embedding(name)
    items.append(
        {
            "id": id,
            "name": name,
            "embedding": dense_embedding,
            "sparse_embedding": sparse_embedding,
        }
    )



output = str(DOCUMENTS_DIR / "items.json") 
# output as a JSONL file and save to the GCS bucket
with open(output, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False) 
# ! gsutil cp items.json $BUCKET_URI


output_path = Path(DOCUMENTS_DIR) / "items.json"

upload_blob(BUCKET_NAME,output_path, "items.json")
