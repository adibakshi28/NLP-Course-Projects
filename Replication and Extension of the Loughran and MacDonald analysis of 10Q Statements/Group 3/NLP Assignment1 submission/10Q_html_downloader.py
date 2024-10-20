import os
import pandas as pd
import requests
import glob

# Read the CIKs from the sp500_CIKS.csv file
sp500_ciks = pd.read_csv("sp500_CIKS.csv")  # Make sure the file path is correct
# sp500_ciks = pd.read_csv("subset_ciks.csv")  # Make sure the file path is correct
sp500_ciks['CIK'] = sp500_ciks['CIK'].astype(str).str.zfill(10)  # Ensure CIKs are zero-padded to 10 digits
cik_list = sp500_ciks['CIK'].tolist()

# Create a request header with a valid user-agent
headers = {'User-Agent': "your-email@example.com"}  # Replace with your actual email

# Define the start and end year for the 10-Q filings you want to download
start_year = 2019
end_year = 2024

# Create a directory to save the downloaded 10-Q filings
download_dir = "downloaded_10Qs"
os.makedirs(download_dir, exist_ok=True)

# Loop through each CIK and fetch its filings
for cik in cik_list:
    try:
        # Get the filing metadata for the company
        filing_metadata_url = f'https://data.sec.gov/submissions/CIK{cik}.json'
        filing_metadata = requests.get(filing_metadata_url, headers=headers)
        filing_metadata.raise_for_status()  # Check for request errors

        # Parse the 10-Q filings from the metadata
        all_filings = pd.DataFrame.from_dict(filing_metadata.json()['filings']['recent'])
        
        # Clean reportDate to ensure no empty or invalid values before filtering
        all_filings = all_filings[all_filings['reportDate'].str.strip() != '']  # Remove rows with empty reportDate
        all_filings['year'] = all_filings['reportDate'].str[:4].astype(int, errors='ignore')  # Extract year safely
        
        # Filter to get only 10-Q forms and within the date range of 2008 to 2018
        ten_q_filings = all_filings[
            (all_filings['form'] == '10-Q') &
            (all_filings['year'] >= start_year) &
            (all_filings['year'] <= end_year)
        ]

        # Display or process the 10-Q filings
        print(f"CIK: {cik} - Found {len(ten_q_filings)} 10-Q filings from {start_year} to {end_year}.")
        print(ten_q_filings[['accessionNumber', 'reportDate', 'primaryDocument']])

        # # Optional: Save the 10-Q data for each company to a CSV
        # ten_q_filings.to_csv(f"{cik}_10Q_filings_2008_2018.csv", index=False)

        # Download each 10-Q filing document in HTML format
        for index, row in ten_q_filings.iterrows():
            try:
                # Construct the URL for the primary document using the accession number
                accession_number = row['accessionNumber'].replace('-', '')
                report_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{row['primaryDocument']}"

                # Request the document
                response = requests.get(report_url, headers=headers)
                response.raise_for_status()

                # Save the document as an HTML file
                file_path = os.path.join(download_dir, f"{cik}_{row['reportDate']}_10Q.html")
                with open(file_path, 'wb') as file:
                    file.write(response.content)

                print(f"Downloaded 10-Q report for CIK {cik} on {row['reportDate']} to {file_path}")

            except Exception as e:
                print(f"Error downloading 10-Q report for CIK {cik}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for CIK {cik}: {e}")

# Function to create a tracking dataframe for downloaded 10-Qs
def create_tracking_dataframe(sp500_ciks, download_dir):
    """
    Create a DataFrame that tracks downloaded 10-Q filings.
    
    Args:
        sp500_ciks (pd.DataFrame): DataFrame containing CIK and Ticker mappings.
        download_dir (str): Directory where 10-Q filings are saved.
        
    Returns:
        pd.DataFrame: DataFrame tracking the downloaded 10-Q filings.
    """
    # List all the HTML files in the downloaded 10-Qs directory
    html_files = glob.glob(os.path.join(download_dir, '*.html'))

    # Prepare a list to hold the tracking information
    tracking_data = []

    # Process each HTML file
    for html_file in html_files:
        # Extract file name
        file_name = os.path.basename(html_file)

        # Extract CIK number (first 10 digits)
        cik = file_name.split('_')[0]

        # Extract report date (second part of the file name)
        report_date = file_name.split('_')[1]

        # Find corresponding ticker for the CIK number
        ticker = sp500_ciks.loc[sp500_ciks['CIK'] == cik, 'Ticker'].values[0] if cik in sp500_ciks['CIK'].values else 'Unknown'

        # Append the data to the tracking list
        tracking_data.append({
            'File Name': file_name,
            'Filing Date': report_date,
            'CIK': cik,
            'Ticker': ticker
        })

    # Create a DataFrame from the tracking data
    tracking_df = pd.DataFrame(tracking_data, columns=['File Name', 'Filing Date', 'CIK', 'Ticker'])

    return tracking_df

# Call the function to create a tracking dataframe
tracking_df = create_tracking_dataframe(sp500_ciks, download_dir)

# Save the tracking dataframe to a CSV file
tracking_df.to_csv('downloaded_10Q_tracking.csv', index=False)

print(tracking_df)