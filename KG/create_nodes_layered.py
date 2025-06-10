from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv
from string import Template

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

        print(df.head)  

        self.df = df
        self.URI = "bolt://localhost:7687"
        self.AUTH = ("neo4j", os.getenv("DB_PASSWORD"))


    def create_chapters(self, tx, chapterName: str, chapterContent: str, embeddings: float, parent: str):
        ### Anchor node as themes
        script="""
        MERGE (a:Themes {name: $parent})

        """
        ### Chapter nodes
        for i in range(self.df.shape[0]-1):
            if "chapter" in str(self.df.iloc[i, 0]).lower():
                script+=""" 
                MERGE (b:Chapter {name: "$name"})
                SET b.content = "$content"
                SET b.content = $embeddings
                MERGE (a)-[r:HAS_THEME]->(b)
                
                """
        cypherScriptTemplate = Template(script)

        cypherScript = cypherScriptTemplate.safe_substitute(content=chapterContent,name=chapterName, parent=parent, embeddings=embeddings)


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
                for index, row in self.df.iterrows():
                    session.execute_write(
                        self.create_chapters(chapterName=row.iloc[0], chapterContent=row.iloc[1], parent="Themes"))
                        self.create_theme()

if __name__ == "__main__":
    GenerateDB().run_scripts