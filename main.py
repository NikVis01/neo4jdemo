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
from neo4j import GraphDatabase

from KG.embedding import SickEmbedder

from KG.query_neo import QueryNeo
from postgresDB.query_postgres import QueryPostgres


class Main():
    def __init__(self):
        self.query = ""
        self.embedder = SickEmbedder(dims=300)
        self.llm = LLM()
        self.search = QueryNeo()

    def neoVectorSearch(self):
        
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        content = self.search.session_execute(embedded_query=embedded_query)
        # content = ""

        return content
    
    def postgresVectorSearch(self):
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        content = self.search.session_execute(embedded_query=embedded_query)
        # content = "
    
    def feedLLM(self, query: str):
        original_query = query

        self.query = query
        
        enhanced_query = self.llm.get_response(f"{self.query}\n" + 
                                               "Use this user query and give a very short info text" +
                                               " yourself. The text should emulate how a textbook " +
                                               "would answer the question or provide info within" +
                                               " a paragraph. Give two or three sentences.")
        
        
        print("Enhanced Query:" + enhanced_query)
        
        self.query = enhanced_query

        content = self.neoVectorSearch()

        prompt = f"{self.query}\n"
        prompt += f"{content}\n"

        # print(prompt)

        response = self.llm.get_response(prompt)

        print("LLM RESPONSE: \n" + response)
        
        return 0
    
if __name__ == "__main__":
    user_query = input("query: ")
    obj = Main()
    obj.feedLLM(user_query)
