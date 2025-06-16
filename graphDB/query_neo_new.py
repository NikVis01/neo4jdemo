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
class QueryNeo():
    def __init__(self):
        self.URI = "bolt://localhost:7687"
        self.USER = "neo4j"
        self.PASSWORD = os.getenv("DB_PASSWORD")
        self.driver = GraphDatabase.driver(self.URI, auth=(self.USER, self.PASSWORD))

    def get_body_text(self, tx, embedded_query: list[float]) -> str: # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
        // Step 1: Start at the most similar Summary node
        CALL db.index.vector.queryNodes('summaryEmbeddingIndex', 1, $queryEmbedding)
        YIELD node AS s1

        WITH s1, [$queryEmbedding] AS queryEmbeddings, [] AS visited, [] AS collectedContent, 0 AS depth

        // Step 2: Traverse up to 4 Summary nodes via similarity edges
        CALL {
        WITH s1, queryEmbeddings, visited, collectedContent, depth
        CALL {
            WITH s1
            MATCH (s1)-[:HAS_CONTENT]->(c:Content)
            RETURN collect(c.content) AS initialContent
        }

        WITH s1 AS current, visited + current AS newVisited, collectedContent + initialContent AS newCollected, 1 AS newDepth
        CALL {
            WITH current
            MATCH (current)-[:SIMILAR_TO]->(next:Summary)
            WHERE NOT next IN newVisited
            WITH next, gds.similarity.cosine(next.embedding, queryEmbeddings[0]) AS score
            ORDER BY score DESC
            LIMIT 1
            RETURN next
        } YIELD next AS s2

        // Step 3: Repeat 3 more times
        CALL {
            WITH s2
            MATCH (s2)-[:HAS_CONTENT]->(c2:Content)
            RETURN collect(c2.content) AS content2
        }

        WITH s2 AS current2, newVisited + s2 AS visited2, newCollected + content2 AS collected2, 2 AS depth2

        CALL {
            WITH current2
            MATCH (current2)-[:SIMILAR_TO]->(s3:Summary)
            WHERE NOT s3 IN visited2
            WITH s3, gds.similarity.cosine(s3.embedding, queryEmbeddings[0]) AS score
            ORDER BY score DESC
            LIMIT 1
            RETURN s3
        } YIELD s3

        CALL {
            WITH s3
            MATCH (s3)-[:HAS_CONTENT]->(c3:Content)
            RETURN collect(c3.content) AS content3
        }

        WITH s3 AS current3, visited2 + s3 AS visited3, collected2 + content3 AS collected3, 3 AS depth3

        CALL {
            WITH current3
            MATCH (current3)-[:SIMILAR_TO]->(s4:Summary)
            WHERE NOT s4 IN visited3
            WITH s4, gds.similarity.cosine(s4.embedding, queryEmbeddings[0]) AS score
            ORDER BY score DESC
            LIMIT 1
            RETURN s4
        } YIELD s4

        CALL {
            WITH s4
            MATCH (s4)-[:HAS_CONTENT]->(c4:Content)
            RETURN collect(c4.content) AS content4
        }

        RETURN collected3 + content4 AS finalCollected
        }

        RETURN {
        collectedContent: finalCollected
        } AS result
        """)


        cypherScript = cypherScriptTemplate.safe_substitute(queryEmbedding=embedded_query)
        result = tx.run(cypherScript)

        result_dict = result.data()[0]["result"]
        top_paragraphs = "\n\n".join(result_dict["collectedContent"])

        # chap_cont = str("Chapter intro: \n" + result_dict["chapterIntro"]) + "\n\n" + "Paragraph content: \n" + str(result_dict["bestParagraph"])+"\n"

        chap_cont = "Collected Content from Top 4 Similar Summary Nodes:\n\n" + top_paragraphs + "\n"

        return chap_cont
    
    def get_text_using_key(self, tx, embedded_keyword: list[float]) -> str: # tx is the transaction object w method run() for cypher scripts in neo4j

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

                        // Step 4: Pick top 3 most relevant paragraphs
                        ORDER BY paraScore DESC
                        LIMIT 3

                        // Step 5: Collect paragraphs, return both
                        WITH chapter.content AS chapterIntro, collect(p.content) AS topParagraphs

                        RETURN {
                        chapterIntro: chapterIntro,
                        topParagraphs: topParagraphs
                        } AS result

                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(embeddedKey=embedded_keyword)
        result = tx.run(cypherScript)
        result_dict = result.data()[0]["result"]

        top_paragraphs = "\n\n".join(result_dict["topParagraphs"])
        print(top_paragraphs)
        #print(type(result_dict))
        chap_cont = str("Chapter intro: \n" + result_dict["chapterIntro"]) + "\n\n" + "Paragraph content: \n" + str(top_paragraphs)+"\n"
        # print(chap_cont)

        #print(result_dict) 

        return chap_cont

    def session_execute(self, embedded_query: list[float]) -> str:
        with self.driver as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                result = session.execute_write(self.get_body_text, embedded_query=embedded_query)
        
        self.driver.close()  

        return result
                

        