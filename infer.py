import openai
from openai import OpenAI
import os

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

### Example query
if __name__ == "__main__":
    LLM().get_response(query="wtf is fishing")