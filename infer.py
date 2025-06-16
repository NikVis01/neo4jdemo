import openai
from openai import OpenAI
import os
import pandas as pd

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLM():
    def __init__(self):
        self.model="o3-mini"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.prompt = """
            You are a graphRAG LLM. You'll receive the necessary info from a tanzanian geography textbook to respond to the user's query.
            The user might ask something like "what's the difference between planted and natural forests" and you will do your utmost to stick to the content you're given.
            Rephrase it to meet the user with efficient and polite manner.

            You'll get the user query along with relevant content from the textbook bellow:
            """
    
    def get_response(self, query: str) -> str:
        print(self.prompt + query)

        response = self.client.responses.create(
        model=self.model,
        input=self.prompt + query
        )

        return response.output_text
    
    def summarize_with_openai(self, texts):
        joined = " ".join(texts)
        prompt = f"""The following paragraphs contain information that belongs to the same
                    groups in a knowledge graph. Give a summary of the most important concepts
                    within the paragraph written in the style of a textbook paragraph. Keep it short,
                    no need for an introduction for the summary. Just write three or four sentences, maximum
                    five if you feel like there is more needed:\n\n{joined}"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response

### Example query
if __name__ == "__main__":
    LLM().get_response(query="wtf is fishing")