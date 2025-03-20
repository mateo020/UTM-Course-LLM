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
    """Get the cache directory =, cretae if doesnt exist"""