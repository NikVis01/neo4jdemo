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

    def get_body_text(self, tx, theme: str): # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
                        MATCH (:Themes)-[:HAS_THEME]->(t:Chapter {name: "$theme"})
                        RETURN t.content
                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(theme=theme)
        result = tx.run(cypherScript)

        return [record.data() for record in result][0]["t.content"] # Decoding output


    def get_nodes(self):
        with self.driver.session() as session:
            nodes = session.execute_read(self.get_body_text) # Don't need to pass tx, session.execute_read injects the parameter
            print(nodes)
            # print(type(nodes))

        self.driver.close()  

obj = QueryDB()
obj.get_nodes()