from llama_cloud_services import LlamaParse
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

class CoolParser():

    def __init__(self, 
                 api_key=api_key, 
                 num_workers: int = 4, 
                 verbose: bool = True, 
                 language: str = "en", 
                 result_type: str = "markdown"):
        
        self.parser = LlamaParse(api_key=api_key, 
                                 num_workers=num_workers, 
                                 verbose=verbose, 
                                 language=language, 
                                 result_type=result_type)
        
    def parse_page(self, file_path):

        try:
            result = self.parser.parse(file_path)
            markdown_documents = result.get_markdown_documents(split_by_page=True)

            # for page in result.pages:
            #     print(page.md)

            return result

        except Exception as e:
            print("Error parsing file:", e)


if __name__ == "__main__":
        
    # Parse a single page
    file_path = "./data/20pagebook.pdf"  # Replace with the path to your PDF file

    parser = CoolParser()
    parsed_data = parser.parse_page(file_path)


    ### MAYBE:
    # Headings & subheadings could be used to navigate the document faster
    # only body text used to extract the main content when the body of text has been identified