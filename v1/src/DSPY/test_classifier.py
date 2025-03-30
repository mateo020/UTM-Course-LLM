import dspy
from pathlib import Path
import os
from dotenv import load_dotenv
import pickle
from typing import Literal
# Load environment variables
load_dotenv()

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Load the optimized classifier
model_path = Path(__file__).parent / "mipro_optimized_classify.json"
if not model_path.exists():
    raise FileNotFoundError(f"Optimized classifier not found at {model_path}")



class Categorize(dspy.Signature):
    """Classify user question."""

    event: str = dspy.InputField()
    category: Literal[
        "Housing & Residence",
        "Career Services & Co-op",
        "Academic Support",
        "Campus Services",
        "Degree Requirements",
        "Course Prerequisites",
        "Course Information",
        "Financial Aid & Tuition"
    ] = dspy.OutputField()
    confidence: float = dspy.OutputField()

# Create non-optimized classifier
non_optimized_classify = dspy.Predict(Categorize)

# Load optimized classifier
optimized_classify = dspy.Predict(Categorize)
optimized_classify.load(model_path)

# Load our model for inference
lm = dspy.LM('ollama_chat/llama3.2', api_base='http://localhost:11434')
dspy.configure(lm=lm)



# Test questions
test_questions = [
    "Can I decorate my dorm room walls with paint or stickers?",
    "Does UofT offer any support for starting a new student business?",
    "Can career services advise me if I'm unsure about my major?",
    "Is there a place on campus to practice presentation skills?",
    "Does the library offer proofreading services for essays?",
    "Will the student health clinic help me get accommodations for anxiety during exams?",
    "Can I request special housing due to allergies or medical needs?",
    "Are there scholarships specifically for international exchange programs?",
    "What happens to my tuition fees if I withdraw halfway through the semester?",
    "Can my AP credits fulfill any course prerequisites?",
]

# Run tests
print("\nRunning classification comparison tests:")
print("=" * 80)
for question in test_questions:
    
    print(f"\nQuestion: {question}")
    print("-" * 80)
    
    # Get non-optimized result
    non_opt_result = non_optimized_classify(event=question)
    print("Non-optimized Classifier:")
    print(f"Category: {non_opt_result.category}")
    print(f"Confidence: {non_opt_result.confidence:.2f}")
    
    # Get optimized result
    opt_result = optimized_classify(event=question)
    print("\nOptimized Classifier:")
    print(f"Category: {opt_result.category}")
    print(f"Confidence: {opt_result.confidence:.2f}")
    
    # Compare results
    print("\nComparison:")
    print(f"Categories match: {non_opt_result.category == opt_result.category}")
    print(f"Confidence difference: {abs(non_opt_result.confidence - opt_result.confidence):.2f}")
    print("=" * 80) 
    print(dspy.inspect_history())