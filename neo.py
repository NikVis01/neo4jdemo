from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "twigaisawesome"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# print(type(driver))

def get_anything(tx): # tx is the transaction object w method run() for cypher scripts in neo4j
    result = tx.run("MATCH (n) RETURN n")
    return [record.data() for record in result]

with driver.session() as session:
    nodes = session.execute_read(get_anything) # Don't need to pass tx, session.execute_read injects the parameter
    print(nodes)

driver.close()