import dspy


class GenerateQuery(dspy.Signature):
    """Given a user's academic question and optional context, generate a focused subquestion or reasoning step 
    that helps answer the original question.

    Use this to decompose multi-step academic questions into intermediate queries.

    Examples:
    Q: What courses are similar to CSC311?
    SubQ: What topics are covered in CSC311?

    Q: Can I take CSC265 without CSC236?
    SubQ: What is the prerequisite requirement for CSC265?

    Q: What course teaches machine learning in Python?
    SubQ: Which courses include Python-based machine learning in their description?

    Avoid repeating the original question. Instead, zoom in on one concept to advance reasoning.
    """
    context = dspy.InputField(desc="may contain relevant context for the question")
    question = dspy.InputField()
    query = dspy.OutputField()

class GenerateAnswer(dspy.Signature):
    """Generate an answer from a given query"""
    context = dspy.InputField(desc="may contain relevant context for the question")
    query = dspy.InputField()
    answer = dspy.OutputField()



class MultiHop(dspy.Module):
    def __init__(self, retriever, passages_per_hop=5, max_hops=5):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateQuery) for _ in range(max_hops)]
        self.retriever = retriever
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.max_hops = max_hops
        self.k = passages_per_hop
        print("--------------------------------")
        print("multihop initialized")
        print("--------------------------------")

    def __call__(self, question: str):
        context = []

        for hop in range(self.max_hops):
            query_response = self.generate_query[hop](question=question, context="\n".join(context))
            query = query_response.query
            print("--------------------------------")
            print(query)
            print("--------------------------------")
            results = self.retriever(query)
            passages = results.get("passages", [])

            context.extend(passages)  # flatten

        pred = self.generate_answer(context="\n".join(context), query=question)
        return dspy.Prediction(context=context, answer=pred.answer)
