import csv
import dspy
from dspy.evaluate import Evaluate
from dspy.teleprompt import *
from typing import Literal
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

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

def validate_category(example, prediction, trace=None):
    return prediction.category == example.category

classify = dspy.Predict(Categorize)

# Get the correct path to the training set
root_dir = Path(__file__).resolve().parents[3]
training_file = root_dir / "v1" / "files" / "academic_assistant_training_set.csv"

# Load the trainset
trainset = []
with open(training_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        example = dspy.Example(event=row['question'], category=row['category']).with_inputs("event")
        trainset.append(example)

# # Evaluate our existing function
# evaluator = Evaluate(devset=trainset, num_threads=1, display_progress=True, display_table=5)
# evaluator(classify, metric=validate_category)

# Load our model
lm = dspy.LM('ollama_chat/llama3.2', api_base='http://localhost:11434')
prompt_gen_lm = dspy.LM('openai/gpt-4o-mini', api_key=OPENAI_API_KEY, max_tokens=3000)

# Configure DSPy with both models
dspy.configure(lm=lm)

# Evaluate our existing function
evaluator = Evaluate(devset=trainset, num_threads=1, display_progress=True, display_table=5)
evaluator(classify, metric=validate_category)

# Optimize
tp = dspy.MIPROv2(metric=validate_category, auto="light", prompt_model=prompt_gen_lm, task_model=lm)
optimized_classify = tp.compile(classify, trainset=trainset, max_labeled_demos=0, max_bootstrapped_demos=0)
optimized_classify.save(f"mipro_optimized_classify.json")

#test
classification = optimized_classify(event="What is the deadline for droooping a course in fall semester?")
print(classification)
