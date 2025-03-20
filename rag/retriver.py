from typing import List
from pathlib import Path
import hashlib
import pickle

import pypdf
from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_core.documents import Document

_global_retriever = None

def get_cache_dir():
    """Get the cache directory, cretae if doesnt exist"""
    cache_dir = Path("cache/rag")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
def compute_files_hash(file_paths: List[str]) -> str:
    """compute hash of the files contents and paths to use as cache key"""
    hasher = hashlib.sha256()
    for file_path in sorted(file_paths):
        try:
            hasher.update(file_path.encode())
            with open(file_path, 'rb') as f:
                #chunck
                for chunk in iter(lambda: f.read(4096),b''):
                    hasher.update(chunk)
        except Exception as e:
            hasher.update(str(e).encode())
    return hasher.hexdigest

def save_rag_cache(file_paths: List[str], vector_store, doc_store):
    """ Save RAG components to cache."""
    try:
        cache_dir = get_cache_dir()
        files_hash = compute_files_hash(file_paths)
        vector_store.save_local(str(cache_dir / f"{files_hash}_vectors"))
        with open(cache_dir/f"{files_hash}_docstore.pkl", 'wb') as f:
            pickle.dump(doc_store,f)
        with open(cache_dir/ f"{files_hash}_files.text", 'w') as f:
            f.write("\n".join(file_paths))
    except Exception as e:
        print(f"Error saving RAG cache: {e}")


def load_rag_cache(file_paths: List[str]) -> tuple:
    try:
        cache_dir = get_cache_dir()
        files_hash = compute_files_hash(file_paths)

        vector_path = cache_dir / f"{files_hash}_vectors"
        docstore_path = cache_dir / f"{files_hash}_docstore.pkl"
        files_path = cache_dir / f"{files_hash}_files.txt"

        #check if cache exists

        #validate file paths havent changed


        
