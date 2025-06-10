import csv
import re
from parser import CoolParser
from io import StringIO

def clean_line(line):
    # Remove boilerplate phrases
    boilerplate_phrases = [
        "PROPERTY OF THE UNITED REPUBLIC OF TANZANIA GOVERNMENT",
        "Student’s Book Form Two Ministry of Education, Science and Technology",
        "Geography for Secondary Schools"
    ]
    for phrase in boilerplate_phrases:
        line = line.replace(phrase, '')
    
    # Remove markdown image syntax and figure references
    if re.match(r'!\[.*\]\(.*\)', line):  # remove image lines
        return ''
    if re.match(r'^\s*(Figure|Fig\.).*', line, re.IGNORECASE):
        return ''
    
    return line.strip()

def markdown_to_csv(markdown_text, csv_path):
    
    lines = markdown_text.splitlines()

    skip_next_lines = 0

    entries = []
    current_heading = None
    current_content = []

    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            continue

        # Check if this line is a figure or contains 'Fig.' or 'Figure'
        if re.search(r'\b(Fig(?:ure)?\.?\s*\d+)', line, re.IGNORECASE):
            skip_next_lines = 2  # also skip 2 lines after figure reference
            continue

        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue

        heading_match = re.match(r'^# (.+)', line)
        if heading_match:
            if current_heading is not None:
                entries.append((current_heading.strip(), ' '.join(current_content).strip()))
            current_heading = heading_match.group(1)
            current_content = []
        elif current_heading:
            current_content.append(line)

    # Don't forget the last entry
    if current_heading is not None:
        entries.append((current_heading.strip(), ' '.join(current_content).strip()))

    # Write to CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for heading, content in entries:
            writer.writerow([heading, content])

if __name__ == "__main__":
    
    file_path = "data/extracted_page1.pdf"  # Replace with the path to your PDF file

    parser = CoolParser()
    parsed_data = parser.parse_page(file_path)

    markdown_to_csv(parsed_data.pages[0].md, 'data/test.csv')
