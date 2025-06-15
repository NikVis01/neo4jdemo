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

from graphDB.embedding import SickEmbedder

from graphDB.query_neo import QueryNeo
from postgresDB.query_postgres import QueryPostgres

import numpy as np

class Main():
    def __init__(self):
        self.query = ""
        self.db_select = ""

        self.embedder = SickEmbedder(dims=300)
        self.llm = LLM()
        self.neo_search = QueryNeo()
        self.post_search = QueryPostgres()

    def neoVectorSearch(self) -> str:
        
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        content = self.neo_search.session_execute(embedded_query=embedded_query)
        # content = ""

        return content
    
    def postgresVectorSearch(self):
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        content = self.post_search.searchDB(query=embedded_query)
        # content = "

        return content
    
    def feedLLM(self, db_select: str, query: str) -> None:
        self.db_select = db_select

        # We should try putting this into the LLM to minimize hallucinations:
        # original_query = query

        self.query = query
        
        enhanced_query = self.llm.get_response(f"{self.query}\n" + 
                                               "Use this user query and give a very short info text" +
                                               " yourself. The text should emulate how a textbook " +
                                               "would answer the question or provide info within" +
                                               " a paragraph. Give two or three sentences.")
        
        
        print("Enhanced Query:" + enhanced_query)
        
        self.query = enhanced_query

        prompt = f"{self.query}\n"

        if db_select == "0":
            neo4j_content = self.neoVectorSearch()
            prompt += f"{neo4j_content}\n"

        elif db_select == "1":
            postgres_content = self.postgresVectorSearch()
            prompt += f"{postgres_content}\n"

        else: 
            print("Dumbass, 0 or 1 it's not that hard")

        response = self.llm.get_response(prompt)

        print("LLM RESPONSE: \n" + response)

    
    def calcCosine(self, str1: str, str2: str) -> int:
        ### Calc cosine similarity between Natural and Planted Forests
        vec1 = np.array(self.embedder.get_embedding_str(str1))
        vec2 = np.array(self.embedder.get_embedding_str(str2))

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        return dot_product / (norm1 * norm2)
    
if __name__ == "__main__":
    obj = Main()

    similarity = obj.calcCosine(str1="",
                   str2="")
    # print(similarity)

    db_select = input("Which DB would you like to use? 0 for neo4j, 1 for Postgres: ")
    user_query = input("Query: ")
    
    obj.feedLLM(db_select=db_select,query=user_query)


