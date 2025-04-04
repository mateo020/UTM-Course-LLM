import dspy


class GenerateQuery(dspy.Signature):
    """Generate a query from input question"""
    context = dspy.InputField(desc="may contain relevant context for the question")
    question = dspy.InputField()
    query = dspy.OutputField()

class GenerateAnswer(dspy.Signature):
    """Generate an answer from a given query"""
    context = dspy.InputField(desc="may contain relevant context for the question")
    query = dspy.InputField()
    answer = dspy.OutputField()



class MultiHop(dspy.Module):
    def __init__(self, retriever, passages_per_hop=10, max_hops=10):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateQuery) for _ in range(max_hops)]
        self.retriever = retriever
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.max_hops = max_hops
        self.k = passages_per_hop

    def forward(self, question: str):
        context = []

        for hop in range(self.max_hops):
            query_response = self.generate_query[hop](question=question, context="\n".join(context))
            query = query_response.query

            results = self.retriever(query)
            passages = results.get("passages", [])

            context.extend(passages)  # flatten

        pred = self.generate_answer(context="\n".join(context), query=question)
        return dspy.Prediction(context=context, answer=pred.answer)
