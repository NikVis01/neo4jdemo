### For vector search in postgres

import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import psycopg2

class QueryPostgres():
    def __init__(self):
        self.query = []

        self.conn = psycopg2.connect(
        dbname="ragdb",
        user=os.getenv("POSTGRES_USER_NAME") ,
        password=os.getenv("POSTGRES_DB_PASS"),
        host="localhost",
        port=5432
        )

        self.cur = self.conn.cursor()

    def searchDB(self, query: list[float]):
        vector_str = f"'[{', '.join(map(str, query))}]'"

        search_script = Template("""
        SELECT id, title, content
        FROM documents
        ORDER BY embedding <#> $query -- query vector goes here dawg
        LIMIT 3;
        """) ### Top-K = 3, one of the strenghts of a simpler postgresDB as opposed to graphDB

        self.cur.execute(search_script.substitute(query=vector_str))
        print(self.cur.fetchall())

        return self.cur.fetchall() ### Should return top 3 k's. 
    