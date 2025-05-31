   # vector_db.py
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
embedding_function = OllamaEmbeddings(model="nomic-embed-text") 
db = Chroma(persist_directory="path/to/chroma_db", embedding_function=embedding_function)