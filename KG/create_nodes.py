from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "bolt://localhost:7687"
AUTH = ("neo4j", os.getenv("DB_PASSWORD"))

def create_chapter(tx, name: str, content: str, parent: str):
    tx.run(
        """
        // Anchor node Themes
        MERGE (a:Themes {name: $parent})

        // Create chapter nodes
        // goes here

        // Create relationship between chapter & anchor
        // goes here

        // Themes stuff - pretty much good
        MERGE (b:Theme {name: $name})
        SET b.content = $content
        MERGE (a)-[r:%s]->(b)
        """ % 'HAS_THEME',
        name=name,
        content=content,
        parent=parent
    )

def create_theme(tx, name: str, content: str, parent: str):
    tx.run("""
           
           """ % 'HAS_SUBTHEME',
           name=name,
           content=content,
           parent=parent)
    
    
with GraphDatabase.driver(URI, auth=AUTH) as driver:

    df = pd.read_csv("./data/test.csv")
    df = pd.concat([df.columns.to_frame().T, df])
    df.columns = range(len(df.columns))
    
    driver.verify_connectivity()
    
    with driver.session() as session:
        for index, row in df.iterrows():
            session.execute_write(create_chapter, row.iloc[0], row.iloc[1], "Themes")

