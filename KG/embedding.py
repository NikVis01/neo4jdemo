import openai
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SickEmbedder():
    def __init__(self):
        self.text="" # Just init empty var
        self.model="text-embedding-3-small"
        self.dims=300 # Should be fine for now (masters in ML told me so)
        
    def get_embedding_str(self, text):
        self.text = text

        self.text = self.text.replace("\n", " ")

        # Debug for embedding object
        # print(client.embeddings.create(input=[self.text], model=self.model, dimensions=self.dims).data[0])

        return client.embeddings.create(input = [self.text], model=self.model).data[0].embedding


    # print(len(embeddings))

# EXAMPLE USAGE:
""" 
obj = SickEmbedder()
obj.get_embedding_str(text="penithe")
"""