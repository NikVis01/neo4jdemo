from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "bolt://localhost:7687"
AUTH = ("neo4j", os.getenv("DB_PASSWORD"))

df = pd.read_csv(".data/test.csv")
df = pd.concat([df.columns.to_frame().T, df])
df.columns = range(len(df.columns))

print(df.head)

def create_relationship(tx, name: str, content: str, parent: str):
    tx.run(
        """
        MERGE (a:Themes {name: $parent})
        MERGE (b:Theme {name: $name})
        SET b.content = $content
        MERGE (a)-[r:%s]->(b)
        """ % 'HAS_THEME',
        name=name,
        content=content,
        parent=parent
    )

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    
    with driver.session() as session:
        for index, row in df.iterrows():
            session.execute_write(create_relationship, row.iloc[0], row.iloc[1], "Themes")

