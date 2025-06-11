from neo4j import GraphDatabase
from string import Template
from dotenv import load_dotenv
import os

load_dotenv()

"""
URI = "bolt://localhost:7687"
USER = "neo4j"
"""

# print(type(driver))
class QueryDB():
    def __init__(self):
        self.URI = "bolt://localhost:7687"
        self.USER = "neo4j"
        self.PASSWORD = os.getenv("DB_PASSWORD")
        self.driver = GraphDatabase.driver(self.URI, auth=(self.USER, self.PASSWORD))

    def get_body_text(self, tx, embedded_query): # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
                        // Step 1: Find the best matching Chapter using ANN
                        CALL db.index.vector.queryNodes('chapterEmbeddingIndex', 1, $queryEmbedding)
                        YIELD node AS chapter, score AS chapterScore

                        // Step 2: Find Paragraphs within that Chapter
                        MATCH (chapter)<-[:IN_CHAPTER]-(p:Paragraph)

                        // Step 3: Compute cosine similarity between each Paragraph and the query
                        WITH p, chapterScore, similarity.cosine(p.embedding, $queryEmbedding) AS paraScore
                        WHERE paraScore IS NOT NULL

                        // Step 4: Return top paragraphs with their scores
                        RETURN p.content AS content, paraScore, chapterScore
                        ORDER BY paraScore DESC
                        LIMIT 5

                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(queryEmbedding=embedded_query)
        result = tx.run(cypherScript)
         
        # return [record.data() for record in result][0]["t.content"] # Decoding output
        return result

    def session_execute(self, embedded_query):
        with self.driver as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                result = session.execute_write(self.get_body_text, embedded_query=embedded_query)
        
        self.driver.close()  

        return result
                

        