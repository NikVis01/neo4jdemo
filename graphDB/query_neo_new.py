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

    ### ----- Narrow Search Algorithm ----- ###
    def get_body_text(self, tx, embedded_query: list[float]) -> str: # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
        // Step 1: Find the most similar :Summary node
        CALL db.index.vector.queryNodes('summary_embedding_index', 1, $queryEmbedding)
        YIELD node AS summary, score

        // Step 2: Traverse child :Concept nodes with top similarity at each level
        CALL (summary) {
        // Level 1
        MATCH (summary)-[:REPRESENTS]->(c1:Concept)
        CALL db.index.vector.queryNodes('concept_embedding_index', 10, $queryEmbedding)
        YIELD node AS candidate1, score AS score1
        WHERE candidate1 = c1
        WITH candidate1 AS concept1
        ORDER BY score1 DESC
        LIMIT 1

        // Level 2
        OPTIONAL CALL (concept1) {
            MATCH (concept1)-[:SIMILAR_TO]->(c2:Concept)
            CALL db.index.vector.queryNodes('concept_embedding_index', 10, $queryEmbedding)
            YIELD node AS candidate2, score AS score2
            WHERE candidate2 = c2 AND elementId(candidate2) <> elementId(concept1)
            WITH candidate2 AS concept2
            ORDER BY score2 DESC
            LIMIT 1
            RETURN concept2
        }

        // Level 3
        OPTIONAL CALL (concept1, concept2) {
            MATCH (concept2)-[:SIMILAR_TO]->(c3:Concept)
            CALL db.index.vector.queryNodes('concept_embedding_index', 10, $queryEmbedding)
            YIELD node AS candidate3, score AS score3
            WHERE candidate3 = c3
            AND elementId(candidate3) <> elementId(concept2)
            AND elementId(candidate3) <> elementId(concept1)
            WITH candidate3 AS concept3
            ORDER BY score3 DESC
            LIMIT 1
            RETURN concept3
        }

        // Return only required paragraph properties
        RETURN
            concept1.paragraph AS paragraph1,
            concept2.paragraph AS paragraph2,
            concept3.paragraph AS paragraph3
        }

        // Final structured return: exclude embeddings entirely
        RETURN {
        summaryContent: summary.summaryText,
        topParagraphs: [paragraph1, paragraph2, paragraph3]
        } AS result
        """)

        cypherScript = cypherScriptTemplate.safe_substitute(queryEmbedding=embedded_query)
        result = tx.run(cypherScript)

        result_dict = result.data()[0]["result"]

        top_paragraphs = "\n\n".join(result_dict["topParagraphs"])

        chap_cont = str("Summary Content: \n" + str(result_dict["summaryContent"]) + "\n\n" + 
                "Paragraph content: \n" + top_paragraphs + "\n")

        # print(chap_cont)
        return chap_cont
    

    ### ----- Shallow Search Algorithm ----- ###
    def get_summary_content(self, tx, embedded_query: list[float]) -> str:
        cypherScriptTemplate = Template("""
        WITH $queryEmbedding AS targetEmbedding
        MATCH (s:Summary)
        WHERE s.embedding IS NOT NULL
        WITH s, gds.similarity.cosine(s.embedding, targetEmbedding) AS score
        RETURN s.summaryText AS summary, score
        ORDER BY score DESC
        LIMIT 3
        """)

        result = tx.run(cypherScriptTemplate.safe_substitute(queryEmbedding=embedded_query))

        results_list = result.data()

        result_str=""
        for i in range(len(results_list)-1):
            result_str += f"Paragraph: {i+1} \n" + results_list[i]["summary"] +f"\n"
 
        print(result_str)
        return result_str            
                                        
    # Currently unused as far as I'm aware:
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
        # print(top_paragraphs)
        # print(type(result_dict))
        chap_cont = str("Chapter intro: \n" + result_dict["chapterIntro"]) + "\n\n" + "Paragraph content: \n" + str(top_paragraphs)+"\n"
        # print(chap_cont)

        # print(result_dict) 

        return chap_cont

    ### For executing NSA
    def session_execute_narrow(self, embedded_query: list[float]) -> str:
        with self.driver as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                result = session.execute_write(self.get_body_text, embedded_query=embedded_query)
        
        self.driver.close()  

        return result
    
    ### For executing SSA
    def session_execute_shallow(self, embedded_query: list[float]) -> str:
        with self.driver as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                result = session.execute_write(self.get_summary_content, embedded_query=embedded_query)
        
        self.driver.close()  

        return result