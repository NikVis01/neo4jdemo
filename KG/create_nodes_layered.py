from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import string
import re


load_dotenv()

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"

"""
URI = "bolt://localhost:7687"
AUTH = ("neo4j", os.getenv("DB_PASSWORD"))

df = pd.read_csv(".data/test.csv")
df = pd.concat([df.columns.to_frame().T, df])
df.columns = range(len(df.columns))
"""

class GenerateDB():
    def __init__(self):
        df = pd.read_csv("./data/test.csv")
        df = pd.concat([df.columns.to_frame().T, df])
        df.columns = range(len(df.columns))
        
        # print(df.head())
        
        self.df = df
        self.URI = "bolt://localhost:7687"
        self.AUTH = ("neo4j", os.getenv("DB_PASSWORD"))

    def create_master_node(self, tx):
        script="""
        MERGE (a:Book {name: "Book"})
        """
        tx.run(script)
        return script

    def create_chapters(self, 
                        tx, 
                        df_row: pd.DataFrame, 
                        embedding: float, 
                        parent_script: str):

        script = parent_script + """
        MERGE (b:Chapter {name: "$name"})
        SET b.content = "$content"
        SET b.embedding = $embedding
        MERGE (a)-[r:HAS_CHAPTER]->(b)
        """
        name=df_row[0]
        content=df_row[1]

        scriptTemp = Template(script)
        realScript = scriptTemp.substitute(name=name,content=content,embedding=embedding)

        tx.run(realScript)

        returned_script = """
        MERGE (a:Chapter {name: "$name"})
        """
        scriptTemp = Template(returned_script)
        returnScript = scriptTemp.substitute(name=name)

        return returnScript

    def create_theme(self, 
                     tx,  
                     df_row: pd.DataFrame,
                     embedding: float, 
                     parent_script: str):

        script = parent_script + """
        MERGE (b:Theme {name: "$name"})
        SET b.content = "$content"
        SET b.embedding = $embedding
        MERGE (a)-[r:HAS_THEME]->(b)
        """
        name=df_row[0]
        content=df_row[1]

        scriptTemp = Template(script)
        realScript = scriptTemp.substitute(name=name,content=content,embedding=embedding)

        tx.run(realScript)
        
    def run_scripts(self):

        with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:

                scriptMaster = session.execute_write(self.create_master_node)

                for i in range(self.df.shape[0]-1):
                    
                    if "chapter" in str(self.df.iloc[i, 0]).lower():
                        chapter_script = session.execute_write(self.create_chapters,
                                                               df_row=self.df.iloc[i, :], 
                                                               embedding=0.1,
                                                               parent_script=scriptMaster)
                    else:
                        session.execute_write(self.create_theme, 
                                              df_row=self.df.iloc[i, :],
                                              embedding=0.1,
                                              parent_script=chapter_script)


if __name__ == "__main__":
    GenerateDB().run_scripts()