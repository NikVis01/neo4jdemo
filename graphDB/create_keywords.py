import pandas as pd
import os
from dotenv import load_dotenv
from string import Template
import string
import re
import openai
from openai import OpenAI

load_dotenv()

class keyword_LLM():

    def __init__(self):

        self.model="o3-mini"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompt = """
        After this information, there is going to be either a short sentence with a prompt or a paragraph of a textbook.
        You are supposed to find one keyword (can be at most three words, but keep it short) in that text and return them to me. The goal is to use 
        words that appear in the text to do a vector search after. Your output should have the following structure and should only be:

        keyword 1

        The input text is:
        """

    def get_keyword(self, user_text: str): # Tf does this return, str? 

        response = self.client.responses.create(
        model=self.model,
        input=self.prompt + user_text
        )

        return response.output_text

 
