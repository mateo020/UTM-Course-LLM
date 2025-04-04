class RAGRetriever:
    def __init__(self, retriever, k=4):
        self.retriever = retriever
        self.k = k

    def __call__(self, query: str):
        try:
            docs = self.retriever.get_relevant_documents(query)
            passages = [doc.page_content for doc in docs[:self.k]]
        except Exception as e:
            print(f"[Retriever error] {e}")
            passages = []
        return {"passages": passages}
