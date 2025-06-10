import csv
import re
from parser import CoolParser
from io import StringIO

def clean_line(line: str) -> str: 
    # Remove boilerplate phrases
    boilerplate_phrases = [
        "PROPERTY OF THE UNITED REPUBLIC OF TANZANIA GOVERNMENT",
        "Student’s Book Form Two Ministry of Education, Science and Technology",
        "# Geography for Secondary Schools",
        "FOR ONLINE USE ONLY",
        "DO NOT DUPLICATE",
        "For Online Use Only"
    ]
    for phrase in boilerplate_phrases:
        line = line.replace(phrase, '')
    
    # Remove markdown image syntax and figure references
    if re.match(r'!\[.*\]\(.*\)', line):  # remove image lines
        return ''
    if re.match(r'^\s*(Figure|Fig\.).*', line, re.IGNORECASE):
        return ''
    
    return line.strip()

def markdown_to_csv(markdown_text: str, 
                    csv_path: str) -> None:
    
    lines = markdown_text.splitlines()
    total_lines = len(lines)
    i = 0
    start_of_book = False
    chapter_count = 0

    skip_next_lines = 0

    entries = []
    current_heading = None
    current_content = []

    while i < total_lines:
        raw_line = lines[i]
        line = clean_line(raw_line)
        if not line:
            i += 1
            continue
        
        if not start_of_book:
            beginning_match = re.match(r'# Chapter One', line)
            if not beginning_match:
                i += 1
                continue
            else:
                chapter_count += 1
            
            if chapter_count == 2:
                start_of_book = True

        # Check if this line is a figure or contains 'Fig.' or 'Figure'
        if re.search(r'\b(Fig(?:ure)?\.?\s*\d+)', line, re.IGNORECASE):
            i += 2
            continue
        
        heading_match = re.match(r'^# (.+)', line)
        if heading_match:
            if current_heading is not None:
                entries.append((current_heading.strip(), ' '.join(current_content).strip()))
            current_heading = heading_match.group(1)
            current_content = []
        elif current_heading:
            current_content.append(line)

        i += 1

    # Don't forget the last entry
    if current_heading is not None:
        entries.append((current_heading.strip(), ' '.join(current_content).strip()))

    # Write to CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for heading, content in entries:
            writer.writerow([heading, content])

if __name__ == "__main__":
    
    file_path = "./data/20pagebook.pdf"  # Replace with the path to your PDF file

    parser = CoolParser()
    parsed_data = parser.parse_page(file_path)

    entire_md = ''

    for page in parsed_data.pages:
        entire_md += page.md

    markdown_to_csv(entire_md, './data/test.csv')
