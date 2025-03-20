import json
def load_cached_embeddings(filename='course_embeddings.json'):
    with open(filename, 'r') as f:
        return json.load(f)

embeddings_dict = load_cached_embeddings()
