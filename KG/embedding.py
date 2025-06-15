import openai
from openai import OpenAI
import os
import pandas as pd

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SickEmbedder():
    def __init__(self, dims):
        self.text="" # Just init empty var
        # self.csv_path = None
        self.model="text-embedding-3-small"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.dims = dims

    def get_embedding_str(self, text: str):
        self.text = text

        self.text = self.text.replace("\n", " ")

        # Debug for embedding object
        # print(client.embeddings.create(input=[self.text], model=self.model, dimensions=self.dims).data[0])

        # print(len(embeddings))

        return self.client.embeddings.create(input = [self.text], model=self.model, dimensions=self.dims).data[0].embedding

    def embed_df(self, input_df):
        df = input_df

        df.fillna('Empty space', inplace=True)

        for i in range(df.shape[0]-1):
            df.iloc[i, 1] = self.get_embedding_str(df.iloc[i, 1])

        return df
    
    def embed_header(self, input_df):

        df = input_df

        for i in range(df.shape[0]-1):
            if not "chapter" in str(df.iloc[i, 0]).lower():
                df.iloc[i, 1] = self.get_embedding_str(df.iloc[i, 0])
            else:
                df.iloc[i, 1] = self.get_embedding_str(df.iloc[i, 0].split(":",1)[1])

        return df

# EXAMPLE USAGE W STRING:
""" 
if __name__ == "__main__":
    obj = SickEmbedder()
    obj.embedd_csv(csv_path="./data/test.csv")
"""

# EXAMPLE USAGE W CSV
if __name__ == "__main__":
    obj = SickEmbedder(dims=300)
    # obj.embedd_df()