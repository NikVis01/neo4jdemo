from PyPDF2 import PdfReader, PdfWriter

def get_page_from_pdf(input_pdf_path, page_number, output_pdf_path="output_page.pdf"):
    try:
        with open(input_pdf_path, 'rb') as input_file:
            reader = PdfReader(input_file)
            num_pages = len(reader.pages)

            if 0 <= page_number < num_pages:
                writer = PdfWriter()
                page = reader.pages[page_number]
                writer.add_page(page)

                with open(output_pdf_path, 'wb') as output_file:
                    writer.write(output_file)
                return True
            else:
                print(f"Error: Page number {page_number + 1} is out of range (1 to {num_pages}).")
                return False
    except FileNotFoundError:
        print(f"Error: Input PDF file not found at '{input_pdf_path}'.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    input_file = "GEOGRAPHY F2 TIE Wazaelimu.com .pdf"  # Replace with the path to your PDF file
    page_to_extract = 11 # Extract the third page (0-based indexing)
    output_file = "./data/extracted_page1.pdf"

    if get_page_from_pdf(input_file, page_to_extract, output_file):
        print(f"Page {page_to_extract + 1} extracted and saved to '{output_file}'")
    else:
        print("Page extraction failed.")
