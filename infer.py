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
            We are performing RAG and will give you a user query with relevant context from a textbook.
            The following will be the user prompt in the beginning and then the relevant context. Answer the
            users query using the provided context. The context consists of several paragraphs of our textbook which
            might (they do not have to) differ in relevance, so not all of it might need to be used or represented in
            your answer. Stay close to the given context, but only use relevant information.

            The user input is:
            """
    
    def get_response(self, query: str) -> str:
        # print(self.prompt + query)

        response = self.client.responses.create(
        model=self.model,
        input=self.prompt + "\n" + query
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