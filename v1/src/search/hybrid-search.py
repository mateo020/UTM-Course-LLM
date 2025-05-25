import json, numpy as np, pandas as pd, scipy.sparse as sp, faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
DOCUMENTS_DIR = ROOT_DIR / "v1" / "files"
data_path = str(DOCUMENTS_DIR / "items.json")                            
with open(data_path, encoding="utf-8") as f:
    items = json.load(f)                               

df = pd.DataFrame(items)                               
dense_mat = np.vstack(df["embedding"]).astype("float32")

# ------- build CSR from the sparse lists -------
rows, cols, data = [], [], []
for r, emb in enumerate(df["sparse_embedding"]):
    rows.extend([r]*len(emb["dimensions"]))
    cols.extend(emb["dimensions"])
    data.extend(emb["values"])

vocab_size = max(cols) + 1
sparse_mat = sp.csr_matrix((data, (rows, cols)), shape=(len(df), vocab_size))


index_dense = faiss.IndexFlatIP(dense_mat.shape[1])
index_dense.add(dense_mat)



MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"    
model = SentenceTransformer(MODEL_ID)

def embed_query_dense(q: str) -> np.ndarray:
    return model.encode([q], normalize_embeddings=True).astype("float32")




vectorizer = TfidfVectorizer().fit(df["name"])
    
def embed_query_sparse(q: str):
    return vectorizer.transform([q])                    # 1×Vocab CSR


def hybrid_search(
    query: str,
    top_k_dense=20,
    top_k_sparse=20,
    w_dense=0.6,
    w_sparse=0.4,
    use_rrf=True,
):
    # -------- dense scores --------
    qd = embed_query_dense(query)
    
    D, I = index_dense.search(qd, top_k_dense)
    dense_scores = {int(i): float(s) for i, s in zip(I[0], D[0])}

    # -------- sparse scores --------
    qs = embed_query_sparse(query)
    sp_scores = (qs @ sparse_mat.T).toarray().ravel()
    top_sparse = sp_scores.argsort()[-top_k_sparse:][::-1]
    sparse_scores = {int(i): float(sp_scores[i]) for i in top_sparse}

    # -------- fusion --------
    if use_rrf:                                          # Reciprocal Rank Fusion
        def rrf(rank): return 1 / (60 + rank)
        all_ids = set(dense_scores) | set(sparse_scores)
        fused = [
            (
                i,
                rrf(list(dense_scores).index(i)) * w_dense
                + rrf(list(sparse_scores).index(i)) * w_sparse
                if i in dense_scores and i in sparse_scores
                else rrf(list(dense_scores).index(i)) * w_dense
                if i in dense_scores
                else rrf(list(sparse_scores).index(i)) * w_sparse
            )
            for i in all_ids
        ]
    else:                                               # simple weighted sum
        all_ids = set(dense_scores) | set(sparse_scores)
        fused = [
            (i, w_dense * dense_scores.get(i, 0) + w_sparse * sparse_scores.get(i, 0))
            for i in all_ids
        ]

    fused.sort(key=lambda x: x[1], reverse=True)
    return [(df.iloc[i]["id"], score) for i, score in fused[:10]]
for cid, score in hybrid_search("data science"):
    print(f"{score:0.3f}", cid)