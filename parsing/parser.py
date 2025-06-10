from llama_cloud_services import LlamaParse
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

class CoolParser():
    def __init__(self, api_key=api_key, num_workers=4, verbose=True, language="en", result_type="markdown"):
        self.parser = LlamaParse(api_key=api_key, num_workers=num_workers, verbose=verbose, language=language, result_type=result_type)
        
    def parse_page(self, file_path):
        try:
            result = self.parser.parse(file_path)
            
            markdown_documents = result.get_markdown_documents(split_by_page=True)

            # get the llama-index text documents
            text_documents = result.get_text_documents(split_by_page=False)

            # get the image documents
            image_documents = result.get_image_documents(
                include_screenshot_images=True,
                include_object_images=False,
                # Optional: download the images to a directory
                # (default is to return the image bytes in ImageDocument objects)
                image_download_dir="./images",
            )

            # access the raw job result
            # Items will vary based on the parser configuration
            for page in result.pages:
                #print(page.text)
                print(page.md)
                #print(page.images)
                #print(page.layout)
                #print(page.structuredData)

            return result

        except Exception as e:
            print("Error parsing file:", e)


if __name__ == "__main__":
        
    # Parse a single page
    file_path = "../data/extracted_page1.pdf"  # Replace with the path to your PDF file

    parser = CoolParser()
    parsed_data = parser.parse_page(file_path)


    ### MAYBE:
    # Headings & subheadings could be used to navigate the document faster
    # only body text used to extract the main content when the body of text has been identified