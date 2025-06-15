### Uploading embeddings and stuff to a postgres table

"""
setup (probably just change sudo apt to brew):

sudo apt update
sudo apt install postgresql postgresql-contrib

psql --version
sudo apt install postgresql-16-pgvector (probably 16 depends on version tho)

sudo apt install postgresql-server-dev-all
sudo -u postgres psql -c "CREATE EXTENSION vector;"

Useful commands:

sudo -u postgres psql (Switch to postgres superuser)

-- CREATE USER N PASS
CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';

-- GOOD TO CHECK
ALTER ROLE <user> CREATEDB;

-- Create DB WITH UR USER
CREATE DATABASE ragdb OWNER <user>;

-- Connect to it and add pgvector extension
backslash+c ragdb

CREATE EXTENSION vector;

-- Exit
backslash+q

-- Test everything works with:
psql -U lethal365 -d ragdb -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Should be ready to go (check if hosted on std port 5432):
psql -U postgres -h localhost -p 5432 -l 

"""

import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import string
import re
import psycopg2

import sys
from pathlib import Path

# Omg importing from another dir is hell tf
sys.path.append(str(Path(__file__).resolve().parents[1]))

from KG.embedding import SickEmbedder

class GeneratePostgres():
    def __init__(self):
        df = pd.read_csv("./data/test.csv")
        df = pd.concat([df.columns.to_frame().T, df])
        df.columns = range(len(df.columns))

        self.dims = 300
        embedder = SickEmbedder(dims=self.dims)

        self.df = df
        self.embedding_df = embedder.embed_df(df.copy())

        self.conn = psycopg2.connect(
        dbname="ragdb",
        user=os.getenv("POSTGRES_USER_NAME") ,
        password=os.getenv("POSTGRES_DB_PASS"),
        host="localhost",
        port=5432
        )

        self.cur = self.conn.cursor()

    def create_and_insert(self):
        # Create table
        create_script = Template("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            title TEXT,
            content TEXT,
            embedding VECTOR($dims)
        );
        """)
        self.cur.execute(create_script.substitute(dims=self.dims))

        # Insert rows
        insert_template = Template("""
        INSERT INTO documents (title, content, embedding)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
        """)
        # print(self.embedding_df)
        for _, row in self.df.iterrows():
            
            title = row[0]
            content = row[1]
            embedding = self.embedding_df.iloc[_, 1] # The embeddings i believe
            self.cur.execute(insert_template.template, (title, content, embedding))

        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == "__main__":
    pg = GeneratePostgres()
    pg.create_and_insert()
    pg.close()

