import dspy

class GenerateQuery(dspy.signature):
    """Generate a query from input question"""
    context = dspy.InputField(desc="may contain relevant context for the question")
    question = dspy.InputField()
    query = dspy.OutputField()

class GenerateAnswer(dspy.signature):
    """Generate an answer from a given query"""
    context = dspy.InputField(desc="may contain relevant context for the question")
    query = dspy.InputField()
    answer = dspy.OutputField()



class MultiHop(dspy.module):
    def __init__(self,passages_per_hop=4,max_hops=4):
        super().__init__()
        self.passages_per_hop = passages_per_hop
        self.max_hops = max_hops

        self.generate_query = dspy.ChainOfThought(GenerateQuery)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

        self.retriever = dspy.Retrieve(k=passages_per_hop)

    def forward(self,question:str):
        context = []
        for hop in range(self.max_hops):
            query_response = self.generate_query[hop](question=question,context=context)
            query = query_response.query
            passages = self.retriever(query).passages
            #cotext = deduplicate(context + passages)
        pred = self.generate_asnwer(context=-context,query=question)
        return dspy.Prediction(context=context,answer=pred.answer)
    