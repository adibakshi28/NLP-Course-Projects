import os
import pandas as pd
import numpy as np

# Function to calculate TF-IDF and proportion weight (using your original logic)
def process_10q_file(file_path):
    # Sample function that returns tfidf_column and proportion_weight_column
    # Replace with actual logic for TF-IDF and proportion weight calculation
    tfidf_column = np.random.random()  # Replace with actual calculation
    proportion_weight_column = np.random.random()  # Replace with actual calculation
    return tfidf_column, proportion_weight_column

# Function to recursively find all 10-Q report files in the directory
def find_all_10Q_reports(root_directory):
    file_paths = []
    
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith('full-submission.txt'):  # Example file name pattern for 10-Q
                full_path = os.path.join(root, file)
                file_paths.append(full_path)
    
    return file_paths

def main(root_directory, output_csv):
    # Find all 10-Q reports
    file_paths = find_all_10Q_reports(root_directory)
    
    results = []
    
    # Process each 10-Q file and store the tfidf and proportion weights
    for idx, file_path in enumerate(file_paths):
        print(f"Processing file {idx + 1}/{len(file_paths)}: {file_path}")
        tfidf_column, proportion_weight_column = process_10q_file(file_path)
        
        # Save the full path for each file instead of just the name
        results.append({
            'File': file_path,  # Save the full path here
            'TF-IDF': tfidf_column,
            'Proportion Weight': proportion_weight_column
        })
    
    # Convert the results into a DataFrame and save as CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"CSV file saved to {output_csv}")

if __name__ == "__main__":
    root_directory = r'C:\Users\max20\Downloads\NLP\sec-edgar-filings'  # Path to 10-Q reports directory
    output_csv = '10Q_TFIDF_ProportionWeight.csv'  # Output CSV file name
    main(root_directory, output_csv)
