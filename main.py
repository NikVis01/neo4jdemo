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

from graphDB.query_neo_new import QueryNeo
from postgresDB.query_postgres import QueryPostgres

import numpy as np

class Main():
    def __init__(self):
        self.query = ""
        self.db_select = ""

        self.embedder = SickEmbedder(dims=1500)
        self.llm = LLM()
        self.neo_search = QueryNeo()
        self.post_search = QueryPostgres()

    def neoVectorSearch(self, search_select: int):
        
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        if search_select == 0:
            content = self.neo_search.session_execute_narrow(embedded_query=embedded_query)
            return content
            # content = ""

        elif search_select == 1:
            content = self.neo_search.session_execute_shallow(embedded_query=embedded_query)
            return content

        else:
            print("WTF")
            return ValueError
    
    def postgresVectorSearch(self):
        embedded_query = self.embedder.get_embedding_str(self.query)
        # print(embedded_query)
        content = self.post_search.searchDB(query=embedded_query)
        # content = "

        return content
    
    def feedLLM(self, db_select: str, query: str, search_select: int) -> None:
        self.db_select = db_select

        # We should try putting this into the LLM to minimize hallucinations:
        # original_query = query
        
        enhanced_query = self.llm.get_response(f"{query}\n" + 
                                               "Use this user query and give a very short info text" +
                                               " yourself. The text should emulate how a textbook " +
                                               "would answer the question or provide info within" +
                                               " a paragraph. Give two or three sentences.")
        
        
        # print("Enhanced Query:" + enhanced_query)
        
        self.query = enhanced_query

        prompt = f"{query}\n"

        if db_select == "0":
            neo4j_content = self.neoVectorSearch(search_select=search_select)
            prompt += f"{neo4j_content}\n"

        elif db_select == "1":
            postgres_content = self.postgresVectorSearch()
            prompt += f"{postgres_content}\n"

        else: 
            print("Dumbass, 0 or 1 it's not that hard")

        response = self.llm.get_response(prompt)

        print("LLM RESPONSE: \n" + response)

    
    def calcCosine(self, str1: str, str2: str) -> int:
        ### Calc cosine similarity between two vectors: For testing
        vec1 = np.array(self.embedder.get_embedding_str(str1))
        vec2 = np.array(self.embedder.get_embedding_str(str2))

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        return dot_product / (norm1 * norm2)
    
if __name__ == "__main__":
    obj = Main()

    db_select = input("Neo4j: 0, Postgres: 1 \nSELECT: ")
    search_selected=int(input("NSA: 0, SSA: 1  \nSELECT: "))
    user_query = input("Query: ")
    
    obj.feedLLM(db_select=db_select,query=user_query,search_select=search_selected)


