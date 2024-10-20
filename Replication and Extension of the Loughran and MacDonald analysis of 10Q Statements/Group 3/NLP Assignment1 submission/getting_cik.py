import pandas as pd
import requests

# Load the Excel file containing the S&P 500 companies
file_path = "sp500_composition.xlsx"  # Update with your file path
sp500_df = pd.read_excel(file_path)

# Extract the tickers from the dataframe
tickers = sp500_df['Ticker'].dropna().unique().tolist()
tickers = [ticker.upper() for ticker in tickers]  # Ensure tickers are uppercase

# Set your user agent
headers = {'User-Agent': 'Your Name (your_email@example.com)'}  # Replace with your actual name and email

# Fetch the ticker to CIK mapping from the SEC website
url = "https://www.sec.gov/files/company_tickers.json"
response = requests.get(url, headers=headers)
data = response.json()

# Create a mapping of tickers to CIKs
ticker_cik_map = {}
for item in data.values():
    ticker = item['ticker'].upper()
    cik = str(item['cik_str']).zfill(10)  # Pad CIK with leading zeros
    ticker_cik_map[ticker] = cik

# Map the tickers to their CIKs
cik_dict = {}
for ticker in tickers:
    if ticker in ticker_cik_map:
        cik_dict[ticker] = ticker_cik_map[ticker]
    else:
        print(f"CIK not found for ticker: {ticker}")

# Convert the dictionary to a DataFrame
cik_df = pd.DataFrame(list(cik_dict.items()), columns=['Ticker', 'CIK'])

# Display the DataFrame
print(cik_df)

cik_df = cik_df.to_csv("sp500_CIKS.csv")