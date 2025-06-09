from neo4j import GraphDatabase
from string import Template

"""
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "twigaisawesome"
"""

# print(type(driver))
class QueryDB():
    def __init__(self): # Make theme passable from LLM output and password an .env var
        self.URI = "bolt://localhost:7687"
        self.USER = "neo4j"
        self.PASSWORD = "twigaisawesome"

        self.driver = GraphDatabase.driver(self.URI, auth=(self.USER, self.PASSWORD))

        self.theme = "Fishing"

    def get_body_text(self, tx): # tx is the transaction object w method run() for cypher scripts in neo4j

        cypherScriptTemplate = Template("""
                        MATCH (:Themes)-[:HAS_THEME]->(t:Theme {name: "$theme"})
                        RETURN t.content
                        """)

        cypherScript = cypherScriptTemplate.safe_substitute(theme=self.theme)

        # print(cypherScript)

        result = tx.run(cypherScript) 
        # print(result)

        return [record.data() for record in result][0]["t.content"] # Decoding output


    def get_nodes(self):
        with self.driver.session() as session:
            nodes = session.execute_read(self.get_body_text) # Don't need to pass tx, session.execute_read injects the parameter
            print(nodes)
            # print(type(nodes))

        self.driver.close()  

obj = QueryDB()
obj.get_nodes()