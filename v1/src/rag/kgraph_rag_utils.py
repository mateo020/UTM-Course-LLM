OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



# Define the graph transformer with allowed entities and relationships


transformer = LLMGraphTransformer(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    strict_mode=True
)
# Process documents to extract graph elements
graph_documents = transformer.convert_to_graph_documents(documents)
# Create a unified graph from the extracted elements
graph = create_graph_from_graph_documents(graph_documents)