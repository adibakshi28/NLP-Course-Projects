import csv
import os
import PyPDF2
import re

def get_text(file_path):
    # Open the PDF file in binary read mode
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ''

        # Iterate through each page in the PDF
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            # Extract text from the current page
            extracted_text = page.extract_text()
            if extracted_text:
                # Replace line breaks and handle hyphenated words
                extracted_text = extracted_text.replace('\n', '')
                # Handle specific hyphenation issues, e.g., change "tues-day" to "tuesday"
                extracted_text = re.sub(r'(\w+)-\s*(\w+)', r'\1\2', extracted_text)
                text += extracted_text + ''

    return text

def filter_text(text):
    # List of keywords
    keywords = [
        "inflation expectation", "interest rate", "bank rate", "fund rate", 
        "economic activity", "inflation", "employment", "unemployment", 
        "growth", "exchange rate", "productivity", "deficit", "demand", "job market", 
        "monetary policy"
    ]

    # Split text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Filter sentences that contain any of the keywords
    filtered_sentences = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]

    return filtered_sentences

def main():
    # Directories containing the PDF files
    dir_paths = ['./data/FOMC_Minutes', './data/FOMC_Presconf', './data/FOMC_Speech']
    for dir_path in dir_paths:
        # Directory to save filtered results
        save_path = dir_path + '_filtered'
        entries = os.listdir(dir_path)
        # Get PDF files from the directory
        file_names = [entry for entry in entries if entry.endswith('.pdf') and os.path.isfile(os.path.join(dir_path, entry))]

        for file_name in file_names:
            file_path = dir_path + '/' + file_name
            csv_save_path = save_path + '/' + file_name.replace('pdf', 'csv')
            text = get_text(file_path)
            filtered_sentences = filter_text(text)

            # Write filtered sentences to a CSV file
            with open(csv_save_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for sentence in filtered_sentences:
                    writer.writerow([sentence])

            print(f"Filtered sentences have been saved to {csv_save_path}.")

if __name__ == '__main__':
    main()
