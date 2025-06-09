from neo4j import GraphDatabase

"""
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "twigaisawesome"
"""

# print(type(driver))
class QueryDB():
    def __init__(self):
        self.URI = "bolt://localhost:7687"
        self.USER = "neo4j"
        self.PASSWORD = "twigaisawesome"

        self.driver = GraphDatabase.driver(self.URI, auth=(self.USER, self.PASSWORD))


    def get_anything(self, tx): # tx is the transaction object w method run() for cypher scripts in neo4j
        result = tx.run(""""
                        // Script for querying
                        """)
        return [record.data() for record in result]


    def get_nodes(self):
        with self.driver.session() as session:
            nodes = session.execute_read(self.get_anything) # Don't need to pass tx, session.execute_read injects the parameter
            print(nodes)


        self.driver.close()  

obj = QueryDB()
obj.get_nodes()