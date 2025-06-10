from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import string


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
        MERGE (a:Themes {name: "Themes"})
        """

        tx.run(script)

    def create_chapters(self, tx, embeddings: float):
        ### Anchor node as themes
        script="""
        MERGE (a:Themes {name: "Theme"})

        """
        literals = list(string.ascii_lowercase)
        # print(literals)

        ### Chapter nodes
        for i in range(self.df.shape[0]-1):
            #print("hello")
            #print(self.df.iloc[i,0])

            if "chapter" in str(self.df.iloc[i, 0]).lower():
                print(self.df.iloc[i,0])
                #print("yes")
                script+=""" 
                MERGE ($literal:Chapter {name: "$name"})
                SET $literal.content = "$content"
                SET $literal.embedding = $embeddings
                MERGE (a)-[r:HAS_THEME]->($literal)
                
                """
                name=self.df.iloc[i,0],
                content=self.df.iloc[i,1],
                literal=literals[i+1]

                scriptTemp = Template(script)
                realScript = scriptTemp.substitute(name=name,content=content,literal=literal,embeddings=0.1)
                print(realScript)
        
        # print(realScript)
        tx.run(realScript)

    def create_theme(self, tx, name: str, content: str, embeddings: float, parent: str):
        ### Theme nodes
        tx.run("""
               
            // Themes stuff - pretty much good
            MERGE (b:Theme {name: $name})
            SET b.content = $content
            MERGE (a)-[r:%s]->(b)
            """ % 'HAS_SUBTHEME',
            name=name,
            content=content,
            parent=parent)
        
    def run_scripts(self):

        with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
            driver.verify_connectivity()
            
            with driver.session() as session:
                session.execute_write(self.create_master_node)
            
                session.execute_write(self.create_chapters, embeddings=0.1)
                #self.create_theme()

if __name__ == "__main__":
    GenerateDB().run_scripts()