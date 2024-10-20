import os
import pandas as pd
import numpy as np
from wrds import Connection
import re

# Load the CIK to PERMNO mapping from the provided CSV file
def load_cik_to_permno_mapping(csv_file_path):
    cik_to_permno = pd.read_csv(csv_file_path)
    # Convert CIK to string and remove leading zeros for consistency
    cik_to_permno['cik'] = cik_to_permno['cik'].apply(lambda x: str(int(x)))
    return cik_to_permno.set_index('cik')['permno'].to_dict()  # Create a CIK-to-PERMNO dictionary

# Function to normalize CIK values
def normalize_cik(cik):
    return str(int(cik))

# Function to extract metadata from inside the 10-Q file
def extract_metadata_10Q(file_content):
    metadata = {}
    
    # Extract CIK
    cik_match = re.search(r'CENTRAL INDEX KEY:\s*(\d+)', file_content)
    if cik_match:
        metadata['CIK'] = normalize_cik(cik_match.group(1))  # Normalize CIK for matching
    
    # Extract Filing Date
    filing_date_match = re.search(r'FILED AS OF DATE:\s*(\d+)', file_content)
    if filing_date_match:
        metadata['Filing Date'] = pd.to_datetime(filing_date_match.group(1), format='%Y%m%d')
    
    return metadata

# Function to get excess returns from CRSP using the PERMNO
def get_excess_returns(conn, permno, filing_date, window=4):
    if permno is None:
        return None
    
    # Query CRSP for stock returns using PERMNO
    query = f"""
        SELECT date, ret
        FROM crsp.dsf
        WHERE permno = '{permno}'
        AND date BETWEEN '{filing_date - pd.Timedelta(days=window)}' AND '{filing_date + pd.Timedelta(days=window)}'
    """
    
    data = conn.raw_sql(query)
    
    # Calculate the 3-day and 4-day excess returns
    data['cum_return_3d'] = data['ret'].rolling(window=3).sum()  # 3-day cumulative return
    excess_return_3d = data['cum_return_3d'].iloc[-3:].sum() if len(data) >= 3 else np.nan
    
    data['cum_return_4d'] = data['ret'].rolling(window=4).sum()  # 4-day cumulative return
    excess_return_4d = data['cum_return_4d'].iloc[-4:].sum() if len(data) >= 4 else np.nan
    
    return excess_return_3d, excess_return_4d

# Function to process a single full-submission.txt file and extract metadata
def process_full_submission_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata including the CIK and filing date
    metadata = extract_metadata_10Q(content)
    
    return metadata

# Main function to process the 10-Q filings and calculate excess returns
def main_10Q_analysis(root_directory, word_list, cik_to_permno):
    # Load the CSV file with TF-IDF and Proportion Weight data
    tfidf_data = pd.read_csv('10Q_TFIDF_ProportionWeight.csv')
    excess_returns = []
    
    # Set up WRDS connection
    conn = Connection(wrds_username='maxshi')
    
    # Process each report from the CSV file
    for idx, row in tfidf_data.iterrows():
        label = row['File']
        
        # Extract the 10-Q file path and process the metadata
        file_path = os.path.join(root_directory, label)
        
        # Progress message
        print(f"Processing file {idx + 1}/{len(tfidf_data)}: {file_path}")
        
        metadata = process_full_submission_file(file_path)
        
        # Get the PERMNO using normalized CIK from the metadata
        cik = metadata['CIK']
        permno = cik_to_permno.get(cik, None)
        
        # Get the filing date from the 10-Q metadata
        filing_date = metadata.get('Filing Date')
        
        if permno and filing_date:
            excess_return_3d, excess_return_4d = get_excess_returns(conn, permno, filing_date)
            excess_returns.append([excess_return_3d, excess_return_4d])
        else:
            excess_returns.append([np.nan, np.nan])
    
    conn.close()
    
    # Convert excess returns to numpy array
    excess_returns = np.array(excess_returns)
    
    # Add 3-day and 4-day excess returns to the existing DataFrame
    tfidf_data['Excess Return 3D'] = excess_returns[:, 0]
    tfidf_data['Excess Return 4D'] = excess_returns[:, 1]
    
    # Save the combined data to a new CSV file
    output_csv = '10Q_TFIDF_ExcessReturns.csv'
    tfidf_data.to_csv(output_csv, index=False)
    
    print(f"Combined CSV file saved to {output_csv}")

if __name__ == "__main__":
    root_directory = r'C:\Users\max20\Downloads\NLP\sec-edgar-filings'
    word_list = {'negative': 0, 'uncertainty': 1, 'litigious': 2}
    
    # Load the CIK to PERMNO mapping from the CSV file
    cik_to_permno = load_cik_to_permno_mapping('S_P_500_Companies_with_PERMNO.csv')
    
    main_10Q_analysis(root_directory, word_list, cik_to_permno)
