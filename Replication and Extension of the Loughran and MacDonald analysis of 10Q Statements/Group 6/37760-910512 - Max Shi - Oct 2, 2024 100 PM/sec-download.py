import json
from sec_edgar_downloader import Downloader
from datetime import datetime

# Load the CIK data from the JSON file
with open('S&P 500 cik.json') as f:
    cik_data = json.load(f)

# Initialize the downloader
dl = Downloader("NYU", "hs4186@nyu.edu")

# Define the start and end years
start_year = 2018
end_year = 2022

# Loop through all companies and download their 10-Q forms
for symbol, cik in cik_data.items():
    print(f"Downloading 10-Q for {symbol} (CIK: {cik})...")
    try:
        # Download 10-Q forms from 2018 to 2022
        dl.get("10-Q", cik, after=f"{start_year}-01-01", before=f"{end_year}-12-31")
    except Exception as e:
        print(f"Error downloading {symbol} (CIK: {cik}): {str(e)}")
