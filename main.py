"""
PROGRAM FLOW:

1. PREPROCESSING:

parsing (/parsing dir) -> embedding (get_embeddings_df in embedding.py) -> generate KG (create_nodes.py)
    I-------------------------------------------------------------------------------I

2. RAG:
query (input main.py) -> embedding (get_embedding_str in embedding.py)-> vector search (neo.py) -> LLM (infer.py) -> response (output main.py)
                                                                                                        I
                                                                                            (query + returned content)
"""


### main.py does not handle preprocessing and creation of graphDB, only processing of query, calling neo.py (vector search) and then feeding into LLM

from infer import LLM
# from KG.neo import QueryDB
from KG.embedding import SickEmbedder

class Main():
    def __init__(self):
        self.query = ""
        self.embedder = SickEmbedder()
        self.llm = LLM()
        # self.search = QueryDB

    def embeddQuery(self):
        self.embedded_query = self.embedder.get_embedding_str(self.query)

        return 0

    def vectorSearch(self):

        # content = self.search.get_body_text(self.embedded_query)

        ### TEMP:
        content = ""

        return content
    
    def feedLLM(self, query: str):
        self.query = query

        self.embeddQuery()
        content = self.vectorSearch()

        prompt = f"{self.query}/n"
        prompt += f"{content}"
        response = self.llm.get_response(prompt)

        print(response)
        
        return 0
    
if __name__ == "__main__":
    user_query = input("query: ")
    obj = Main()
    obj.feedLLM(user_query)
    