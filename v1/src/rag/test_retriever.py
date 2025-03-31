import unittest
from pathlib import Path
import os
from dotenv import load_dotenv
from ..rag.retriever import setup_rag, get_relevant_context, set_rag_retriever

class TestRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that can be reused across tests."""
        load_dotenv()
        
        # Get the absolute path to the course_data.txt file
        root_dir = Path(__file__).resolve().parents[3]
        documents_dir = root_dir / "backend" / "files"
        course_data_path = documents_dir / "course_data.txt"
        
        print(f"Setting up RAG with file: {course_data_path}")
        print(f"File exists: {course_data_path.exists()}")
        
        # Initialize the RAG retriever
        retriever = setup_rag([str(course_data_path)])
        print(f"Retriever created: {retriever is not None}")
        set_rag_retriever(retriever)

    def test_basic_retrieval(self):
        """Test basic retrieval functionality."""
        query = "What are the prerequisites for CSC108?"
        print(f"\nTesting query: {query}")
        context = get_relevant_context(query)
        
        print(f"Context received: {context[:100]}...")  # Print first 100 chars
        
        # Check that we got some context back
        self.assertIsNotNone(context)
        self.assertIsInstance(context, str)
        self.assertGreater(len(context), 0)
        
        # Check that the context contains relevant information
        self.assertIn("CSC108", context)
        self.assertIn("prerequisites", context.lower())

    def test_empty_query(self):
        """Test handling of empty queries."""
        context = get_relevant_context("")
        self.assertEqual(context, "")

    def test_nonexistent_course(self):
        """Test query for a nonexistent course."""
        query = "What are the prerequisites for XYZ999?"
        context = get_relevant_context(query)
        self.assertEqual(context, "")

    def test_specific_course_info(self):
        """Test retrieval of specific course information."""
        query = "What is the course code for Introduction to Computer Programming?"
        context = get_relevant_context(query)
        self.assertIn("CSC108", context)

    def test_multiple_results(self):
        """Test that we get multiple relevant results."""
        query = "What are the prerequisites for computer science courses?"
        context = get_relevant_context(query)
        
        # Check that we have multiple numbered contexts
        self.assertIn("[1]", context)
        self.assertIn("[2]", context)
        self.assertIn("[3]", context)
        self.assertIn("[4]", context)

    def test_special_characters(self):
        """Test handling of queries with special characters."""
        query = "What are the prerequisites for CSC108H5?"
        context = get_relevant_context(query)
        self.assertIn("CSC108H5", context)

    def test_long_query(self):
        """Test handling of long queries."""
        query = "What are the prerequisites and course requirements for CSC108 Introduction to Computer Programming at UTM?"
        context = get_relevant_context(query)
        self.assertGreater(len(context), 0)
        self.assertIn("CSC108", context)

    def test_no_relevant_context(self):
        """Test query that should have no relevant context."""
        query = "What is the weather like in Toronto?"
        context = get_relevant_context(query)
        self.assertEqual(context, "")

if __name__ == '__main__':
    unittest.main() 