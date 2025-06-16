from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import string
import re
from embedding import SickEmbedder

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from neo4j.exceptions import ClientError

load_dotenv()

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"

"""
URI = "bolt://localhost:7687"
AUTH = ("neo4j", os.getenv("DB_PASSWORD"))

df = pd.read_csv(".data/test.csv")
df = pd.concat([df.columns.to_frame().T, df])
df.columns = range(len(df.columns))
"""

class GenerateNeo():
    def __init__(self):
        ### Preprocessing
        df = pd.read_csv("./data/test.csv")
        df = pd.concat([df.columns.to_frame().T, df])
        df.columns = range(len(df.columns))

        ### Generate embedding df
        embedder = SickEmbedder(dims=1500)
        
        self.df = df
        self.embedding_df = embedder.embed_df(df.copy())
        self.header_df = embedder.embed_header(df.copy())
        self.URI = "bolt://localhost:7687"
        self.AUTH = ("neo4j", os.getenv("DB_PASSWORD"))


    def create_relation_df(self, threshold: float = 0.3, top_k: int = 3) -> pd.DataFrame:

        embeddings = np.stack(self.embedding_df.iloc[:, 1].to_list())
        similarity_matrix = cosine_similarity(embeddings)

        edges = []

        for i in range(len(self.embedding_df)):
            sims = similarity_matrix[i]
            top_indices = sims.argsort()[-(top_k+1):-1][::-1]

            for j in top_indices:
                if sims[j] >= threshold:
                    edges.append((self.df.iloc[i, 0], self.df.iloc[j, 0], sims[j]))

        edges_df = pd.DataFrame(edges, columns=["source", "target", "score"])

        return edges_df


    def clear_db(self, tx) -> None:
        tx.run("""
        MATCH(n)
        DETACH DELETE n;
        """)


    def create_node(self,tx, title, paragraph, embedding) -> None:
        tx.run("""
            MERGE (n:Concept {title: $title})
            SET n.paragraph = $paragraph
            SET n.embedding = $embedding
        """, title=title, paragraph=paragraph, embedding=embedding)


    def create_vindex(self,tx) -> None:
        tx.run("""
        CREATE VECTOR INDEX concept_embedding_index
        FOR (n:Concept) ON (n.embedding)
        OPTIONS { indexConfig: {
        `vector.dimensions`: 1500,
        `vector.similarity_function`: "cosine"
        }}
        """)


    def create_edges(self, tx, source, target, score) -> None:
        tx.run("""
        MATCH (a:Concept {title: $source}), (b:Concept {title: $target})
        MERGE (a)-[:SIMILAR_TO {score: $score}]->(b)
        """, source=source, target=target, score=score)


    def create_catalog(self, tx) -> None:
        tx.run("""
        MATCH (source:Concept)-[r:SIMILAR_TO]->(target:Concept)
        RETURN gds.graph.project(
        'myGraph',
        source,
        target,
        {
            relationshipProperties: r { .score }
        },
        { undirectedRelationshipTypes: ['*'] }
        )
        """)


    def clear_catalog(self, tx) -> None:
        # Clears old graph catalog for commnityid generation to reinitialize with valid new node ids
        tx.run("""
        CALL gds.graph.drop('myGraph', false) YIELD graphName
        """)


    def leiden_grouping(self, tx) -> None:
        # OBS: Make sure that the line: 
        # dbms.security.procedures.unrestricted=apoc.*,gds.util,*
        # In DSBM settings is configured as written (allowed gds utils)
        tx.run("""
        CALL gds.leiden.stream('myGraph', { randomSeed: 19 })
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).title AS title, communityId
        ORDER BY title ASC
        """)
        tx.run("""
        CALL gds.leiden.write('myGraph', { writeProperty: 'communityId', randomSeed: 19 })
        YIELD communityCount, nodePropertiesWritten
        """)


    def add_labels(self, tx):
        tx.run("""
        MATCH (n:Concept)
        WHERE n.communityId IS NOT NULL
        WITH n, 'Community_' + toString(toInteger(n.communityId)) AS labelName
        CALL apoc.create.addLabels(n, [labelName]) YIELD node
        RETURN count(*)
        """)


    def label_hierarchy(self, tx):
        tx.run("""
        MATCH (n:Concept)
        REMOVE n:Concept
        SET n:Concept
        """)
        

    ### ---- RUNNING SCRIPTS SEQUENTIALLY ---- ###
    def run_scripts(self) -> None:
        with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
            driver.verify_connectivity()

            # Clearing DB of junk
            with driver.session() as session:
                session.execute_write(self.clear_db)

            print("LOG: DB cleared of old nodes and realtions. Indexes and graph tables might still exist.")

            try:
                # Creating nodes and vector indexes
                with driver.session() as session:
                    for i in range(self.df.shape[0]):
                        session.execute_write(self.create_node, self.df.iloc[i, 0], self.df.iloc[i, 1], self.embedding_df.iloc[i, 1])
                    session.execute_write(self.create_vindex)

                print("LOG: Vindex Created.")

            except ClientError:
                # Vector index probably already exists
                print("LOG: Vindex already exists, check its the newest version, otherwise drop manually and restart.")
                pass

            # Creating edge relationships
            with driver.session() as session:
                for _, row in self.create_relation_df().iterrows():
                    session.execute_write(
                        self.create_edges,
                        row['source'], row['target'], float(row['score'])
                    )

            print("LOG: Edge relations created.")

            # Creating graph catalog for Liden method later
            with driver.session() as session:
                try:
                    session.execute_write(
                        self.create_catalog
                    )

                    print("LOG: Graph Catalog created.")

                except ClientError:
                    # Might already exist and that's fine
                    print("LOG: Graph Catalog already exists.")
                    pass

            try:
                with driver.session() as session:
                    session.execute_write(
                        self.clear_catalog
                    )
                    print("LOG: Old graph catalog cleared.")

            except ClientError:
                # Turns out the graph catalog didn't exist before so we skip clearing it.
                pass

            with driver.session() as session:
                session.execute_write(
                    self.leiden_grouping
                )
                print("LOG: Leiden Grouping completed, new catalog instantiated and community ids written as node properties.")

            with driver.session() as session:
                session.execute_write(
                    self.add_labels
                )
                print("LOG: Community Labels added.")

            with driver.session() as session:
                session.execute_write(
                    self.label_hierarchy
                )
                print("LOG: Label Hierarchy established.")

            print("LOG: SUCCESS! Graph has been initialized. Closing driver...")

            driver.close()


if __name__ == "__main__":
    obj = GenerateNeo()
    obj.run_scripts()