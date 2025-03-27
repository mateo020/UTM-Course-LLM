from pathlib import Path
from rag.retriever import setup_rag, set_rag_retriever
from dotenv import load_dotenv

def main():
    load_dotenv()# Get the path to course_data.txt
    file_path = Path(__file__).parent.parent / "files" / "course_data.txt"
    
    # Set up RAG with the course data file
    retriever = setup_rag([str(file_path)])
    
    # Set the global retriever
    set_rag_retriever(retriever)
    
    print("RAG system has been set up successfully!")

if __name__ == "__main__":
    main() 