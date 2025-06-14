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
                        // Step 1: Find the top-1 best matching Chapter
                        CALL db.index.vector.queryNodes('chapterEmbeddingIndex', 1, $queryEmbedding)
                        YIELD node AS chapter, score AS chapterScore

                        // Step 2: Match paragraphs (Theme nodes) within that Chapter
                        MATCH (chapter)-[:HAS_THEME]->(p:Theme)

                        // Step 3: Score each paragraph for relevance
                        WITH chapter, chapterScore, p,
                            gds.similarity.cosine(p.embedding, $queryEmbedding) AS paraScore
                        WHERE paraScore IS NOT NULL

                        // Step 4: Pick only the most relevant paragraph
                        ORDER BY paraScore DESC
                        LIMIT 1

                        // Step 5: Return both in a dictionary
                        RETURN {
                        chapterIntro: chapter.content,
                        bestParagraph: p.content
                        } AS result

                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(queryEmbedding=embedded_query)
        result = tx.run(cypherScript)
        result_dict = result.data()[0]["result"]

        #print(type(result_dict))
        chap_cont = str("Chapter intro: \n" + result_dict["chapterIntro"]) + "\n\n" + "Paragraph content: \n" + str(result_dict["bestParagraph"])+"\n"
        # print(chap_cont)

        #print(result_dict) 

        return chap_cont
    
    def get_text_using_key(self, tx, embedded_keyword): # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
                        // Step 1: Find the top-1 best matching Chapter
                        CALL db.index.vector.queryNodes('chapterKeyIndex', 1, $embeddedKey)
                        YIELD node AS chapter, score AS chapterScore

                        // Step 2: Match paragraphs (Theme nodes) within that Chapter
                        MATCH (chapter)-[:HAS_THEME]->(p:Theme)

                        // Step 3: Score each paragraph for relevance
                        WITH chapter, chapterScore, p,
                            gds.similarity.cosine(p.keyword, $embeddedKey) AS paraScore
                        WHERE paraScore IS NOT NULL

                        // Step 4: Pick only the most relevant paragraph
                        ORDER BY paraScore DESC
                        LIMIT 1

                        // Step 5: Return both in a dictionary
                        RETURN {
                        chapterIntro: chapter.content,
                        bestParagraph: p.content
                        } AS result

                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(embeddedKey=embedded_keyword)
        result = tx.run(cypherScript)
        result_dict = result.data()[0]["result"]

        #print(type(result_dict))
        chap_cont = str("Chapter intro: \n" + result_dict["chapterIntro"]) + "\n\n" + "Paragraph content: \n" + str(result_dict["bestParagraph"])+"\n"
        # print(chap_cont)

        #print(result_dict) 

        return chap_cont

    def session_execute(self, embedded_query):
        with self.driver as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                result = session.execute_write(self.get_body_text, embedded_query=embedded_query)
        
        self.driver.close()  

        return result
                

        