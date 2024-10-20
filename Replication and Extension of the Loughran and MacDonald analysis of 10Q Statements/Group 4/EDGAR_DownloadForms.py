#!/usr/bin/python
"""
    Program to download EDGAR files by form type
    ND-SRAF / McDonald : 201606
    https://sraf.nd.edu
    Dependencies (i.e., modules you must already have downloaded)
      EDGAR_Forms.py
      EDGAR_Pac.py
      General_Utilities.py
"""

import os
import time
import sys
# Since these imports are dynamically mapped your IDE might flag an error...it's OK
import EDGAR_Forms  # This module contains some predefined form groups
import EDGAR_Pac
import General_Utilities
import requests



# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * +

#  NOTES
#        The EDGAR archive contains millions of forms.
#        For details on accessing the EDGAR servers see:
#          https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm
#        From that site:
#            "To preserve equitable server access, we ask that bulk FTP
#             transfer requests be performed between 9 PM and 6 AM Eastern 
#             time. Please use efficient scripting, downloading only what you
#             need and space out requests to minimize server load."
#        Note that the program will check the clock every 10 minutes and only
#            download files during the appropriate time.
#        Be a good citizen...keep your requests targeted.
#
#        For large downloads you will sometimes get a hiccup in the server
#            and the file request will fail.  These errs are documented in
#            the log file.  You can manually download those files that fail.
#            Although I attempt to work around server errors, if the SEC's server
#            is sufficiently busy, you might have to try another day.
#
#       For a list of form types and counts by year:
#         "All SEC EDGAR Filings by Type and Year"
#          at https://sraf.nd.edu/textual-analysis/resources/#All%20SEC%20EDGAR%20Filings%20by%20Type%20and%20Year


# -----------------------
# User defined parameters
# -----------------------

# List target forms as strings separated by commas (case sensitive) or
#   load from EDGAR_Forms.  (See EDGAR_Forms module for predefined lists.)
PARM_FORMS = EDGAR_Forms.f_10Q # or, for example, PARM_FORMS = ['8-K', '8-K/A']
PARM_BGNYEAR = 2018  # User selected bgn period.  Earliest available is 1994
PARM_ENDYEAR = 2022  # User selected end period.
PARM_BGNQTR = 1  # Beginning quarter of each year
PARM_ENDQTR = 4  # Ending quarter of each year
# Path where you will store the downloaded files
PARM_PATH = r'output\\'
# Change the file pointer below to reflect your location for the log file
#    (directory must already exist)
PARM_LOGFILE = (r'output\EDGAR_Download_FORM-X_LogFile_' + str(PARM_BGNYEAR) + '-' + str(PARM_ENDYEAR) + '.log')
# EDGAR parameter
PARM_EDGARPREFIX = 'https://www.sec.gov/Archives/'


#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * +


# def download_forms():

#     # Download each year/quarter master.idx and save record for requested forms
#     f_log = open(PARM_LOGFILE, 'a')
#     f_log.write('BEGIN LOOPS:  {0}\n'.format(time.strftime('%c')))
#     n_tot = 0
#     n_errs = 0
#     for year in range(PARM_BGNYEAR, PARM_ENDYEAR + 1):
#         for qtr in range(PARM_BGNQTR, PARM_ENDQTR + 1):
#             startloop = time.process_time()
#             n_qtr = 0
#             file_count = {}
#             # Setup output path
#             path = '{0}{1}\\QTR{2}\\'.format(PARM_PATH, str(year), str(qtr))
#             if not os.path.exists(path):
#                 os.makedirs(path)
#                 print('Path: {0} created'.format(path))
#             masterindex = EDGAR_Pac.download_masterindex(year, qtr, True)
#             # masterindex = list(filter(lambda x: x.name.startswith('BANK'), masterindex))
#             if masterindex:
#                 for item in masterindex[:100]:
#                     # while EDGAR_Pac.edgar_server_not_available(True):  # kill time when server not available
#                     #     pass
#                     if item.form in PARM_FORMS:
#                         n_qtr += 1
#                         # Keep track of filings and identify duplicates
#                         fid = str(item.cik) + str(item.filingdate) + item.form
#                         if fid in file_count:
#                             file_count[fid] += 1
#                         else:
#                             file_count[fid] = 1
#                         # Setup EDGAR URL and output file name
#                         #https://www.sec.gov/Archives/edgar/data/70858/000007085818000009/Financial_Report.xlsx
#                         url = PARM_EDGARPREFIX + item.path
#                         fname = (path + str(item.filingdate) + '_' + item.form.replace('/', '-') + '_' +
#                                  item.path.replace('/', '_'))
#                         fname = fname.replace('.txt', '_' + str(file_count[fid]) + '.txt')
#                         print(url)
#                         return_url = General_Utilities.download_to_file(url, fname, f_log)
#                         if return_url:
#                             n_errs += 1
#                         n_tot += 1
#                         # time.sleep(1)  # Space out requests
#             print(str(year) + ':' + str(qtr) + ' -> {0:,}'.format(n_qtr) + ' downloads completed.  Time = ' +
#                   time.strftime('%H:%M:%S', time.gmtime(time.process_time() - startloop)) +
#                   ' | ' + time.strftime('%c'))
#             f_log.write('{0} | {1} | n_qtr = {2:>8,} | n_tot = {3:>8,} | n_err = {4:>6,} | {5}\n'.
#                         format(year, qtr, n_qtr, n_tot, n_errs, time.strftime('%c')))

#             f_log.flush()

#     print('{0:,} total forms downloaded.'.format(n_tot))
#     f_log.write('\n{0:,} total forms downloaded.'.format(n_tot))

#WORKING CODE!!
# EDGAR_DownloadForms.py
# import requests
# import pandas as pd
# import os
# from bs4 import BeautifulSoup
# from time import sleep

# # Function to download the CIK lookup file from SEC
# def download_cik_lookup():
#     url = 'https://www.sec.gov/include/ticker.txt'
#     response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    
#     if response.status_code == 200:
#         with open('cik_lookup.txt', 'wb') as f:
#             f.write(response.content)
#         print("Downloaded CIK lookup file.")
#     else:
#         print(f"Failed to download CIK lookup file. Status code: {response.status_code}")

# # Function to scrape S&P 500 tickers from Wikipedia
# def get_sp500_tickers():
#     url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch S&P 500 tickers. Status code: {response.status_code}")

#     soup = BeautifulSoup(response.content, 'html.parser')
#     table = soup.find('table', {'id': 'constituents'})  # The table on Wikipedia containing the tickers
    
#     sp500_tickers = []
#     for row in table.find_all('tr')[1:]:
#         ticker = row.find_all('td')[0].text.strip()  # First column contains the ticker symbol
#         sp500_tickers.append(ticker)
    
#     return sp500_tickers

# # Function to map S&P 500 tickers to CIKs and save to ticker.txt
# def generate_ticker_file():
#     # Step 1: Download the CIK lookup file from the SEC
#     download_cik_lookup()
    
#     # Step 2: Load CIK lookup into a dataframe
#     cik_lookup_df = pd.read_csv('cik_lookup.txt', sep='\t', header=None, names=['ticker', 'cik'])
    
#     # Step 3: Fetch S&P 500 tickers from Wikipedia
#     sp500_tickers = get_sp500_tickers()

#     # Ensure sp500_tickers is a list and not a string
#     if isinstance(sp500_tickers, str):
#         sp500_tickers = [sp500_tickers]  # Convert single string to list

#     # Step 4: Filter the CIK lookup file for only S&P 500 companies
#     sp500_cik_df = cik_lookup_df[cik_lookup_df['ticker'].isin(sp500_tickers)]
    
#     # Step 5: Save the filtered data to ticker.txt
#     sp500_cik_df.to_csv('ticker.txt', columns=['cik'], index=False)
#     print("Saved S&P 500 CIKs to ticker.txt.")

# # Function to download a file from the SEC
# def download_file(url, save_path):
#     response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
#     if response.status_code == 200:
#         with open(save_path, 'wb') as f:
#             f.write(response.content)
#         print(f"Downloaded {save_path}")
#     else:
#         print(f"Failed to download {url}. Status code: {response.status_code}")

# # Function to download forms for S&P 500 companies from the master index
# def download_sp500_forms(master_index_file, sp500_ciks, start_year, end_year):
#     df = pd.read_csv(master_index_file)
    
#     # Create directory to store downloads if it doesn't exist
#     if not os.path.exists('downloads'):
#         os.makedirs('downloads')
    
#     # Filter the dataframe for the relevant criteria
#     filtered_df = df[(df['cik'].isin(sp500_ciks)) & 
#                      (df['form'] == '10-Q') & 
#                      (df['filing_date'].str[:4].astype(int).between(start_year, end_year))]
    
#     print(f"Found {len(filtered_df)} 10-Q filings for S&P 500 companies between {start_year} and {end_year}.")

#     # Download each filing
#     for _, row in filtered_df.iterrows():
#         cik = row['cik']
#         filing_date = row['filing_date']
#         file_path = row['path']
#         company_name = row['name']
        
#         # Construct the full URL for the filing
#         url = f"https://www.sec.gov/Archives/{file_path}"
#         save_path = f"downloads/{cik}_{filing_date}_10-Q.txt"
        
#         # Download the file
#         download_file(url, save_path)
        
#         # Sleep between downloads to avoid overwhelming SEC servers
#         sleep(1)  # 1 second delay between downloads

# # Function to load S&P 500 CIKs from a ticker file (assumed CSV format)
# def read_sp500_ciks(ticker_file):
#     ticker_df = pd.read_csv(ticker_file)
#     return set(ticker_df['cik'])

# # Example usage
# if __name__ == '__main__':
#     # Step 1: Generate the ticker.txt file containing S&P 500 CIKs
#     generate_ticker_file()  # This will download the CIKs for S&P 500 companies

#     # Step 2: Read S&P 500 CIKs from the generated ticker.txt
#     sp500_ciks = read_sp500_ciks('ticker.txt')

#     # Step 3: Set the master index file (generated by EDGAR_Pac.py)
#     master_index_file = 'master_index.csv'  # The consolidated master index from EDGAR_Pac

#     # Step 4: Download 10-Q forms for the past 5 years (adjust as needed)
#     download_sp500_forms(master_index_file, sp500_ciks, start_year=2019, end_year=2024)
    
#     print("10-Q forms download completed.")

import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
from time import sleep

# Function to download the CIK lookup file from SEC
def download_cik_lookup():
    url = 'https://www.sec.gov/include/ticker.txt'
    response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    
    if response.status_code == 200:
        with open('cik_lookup.txt', 'wb') as f:
            f.write(response.content)
        print("Downloaded CIK lookup file.")
    else:
        print(f"Failed to download CIK lookup file. Status code: {response.status_code}")

# Function to scrape S&P 500 tickers from Wikipedia
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch S&P 500 tickers. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})  # The table on Wikipedia containing the tickers
    
    sp500_tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()  # First column contains the ticker symbol
        sp500_tickers.append(ticker)
    
    return sp500_tickers

# Function to map S&P 500 tickers to CIKs and save to ticker.txt
def generate_ticker_file():
    # Step 1: Download the CIK lookup file from the SEC
    download_cik_lookup()
    
    # Step 2: Load CIK lookup into a dataframe
    cik_lookup_df = pd.read_csv('cik_lookup.txt', sep='\t', header=None, names=['ticker', 'cik'])
    
    # Convert tickers to uppercase as SEC CIK file uses uppercase tickers
    cik_lookup_df['ticker'] = cik_lookup_df['ticker'].str.upper()
    
    # Step 3: Fetch S&P 500 tickers from Wikipedia
    sp500_tickers = get_sp500_tickers()
    sp500_tickers = [ticker.upper() for ticker in sp500_tickers]  # Ensure uppercase

    # Step 4: Filter the CIK lookup file for only S&P 500 companies
    sp500_cik_df = cik_lookup_df[cik_lookup_df['ticker'].isin(sp500_tickers)]
    
    if sp500_cik_df.empty:
        print("No matching CIKs found for S&P 500 tickers.")
    else:
        # Step 5: Save the filtered data to ticker.txt
        sp500_cik_df.to_csv('ticker.txt', columns=['cik'], index=False)
        print(f"Saved {len(sp500_cik_df)} S&P 500 CIKs to ticker.txt.")

# Function to download a file from the SEC
def download_file(url, save_path):
    response = requests.get(url, headers={"User-Agent": "Your Name (your-email@example.com)"})
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {save_path}")
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")

# Function to download forms for S&P 500 companies from the master index
def download_sp500_forms(master_index_file, sp500_ciks, start_year, end_year):
    df = pd.read_csv(master_index_file)
    
    # Create directory to store downloads if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    # Filter the dataframe for the relevant criteria
    filtered_df = df[(df['cik'].isin(sp500_ciks)) & 
                     (df['form'] == '10-Q') & 
                     (df['filing_date'].str[:4].astype(int).between(start_year, end_year))]
    
    print(f"Found {len(filtered_df)} 10-Q filings for S&P 500 companies between {start_year} and {end_year}.")
    
    # Download each filing
    for _, row in filtered_df.iterrows():
        cik = row['cik']
        filing_date = row['filing_date']
        file_path = row['path']
        company_name = row['name']
        
        # Construct the full URL for the filing
        url = f"https://www.sec.gov/Archives/{file_path}"
        save_path = f"downloads/{cik}_{filing_date}_10-Q.txt"
        
        # Download the file
        if not os.path.exists(save_path):
            # Download the file if it doesn't exist
            download_file(url, save_path)
            print(f"Downloaded: {save_path}")
            # Sleep between downloads to avoid overwhelming SEC servers
            sleep(1)  # 1 second delay between downloads
        else:
            print(f"File already exists: {save_path}, skipping download.")
        
        # Sleep between downloads to avoid overwhelming SEC servers
        sleep(1)  # 1 second delay between downloads

    return len(filtered_df)  # Return the number of downloaded filings

# Function to load S&P 500 CIKs from a ticker file (assumed CSV format)
def read_sp500_ciks(ticker_file):
    ticker_df = pd.read_csv(ticker_file)
    return set(ticker_df['cik'])

# Final check for total number of downloaded files
def check_downloaded_files():
    downloaded_files = os.listdir('downloads')
    print(f"Total files downloaded: {len(downloaded_files)}")
    return len(downloaded_files)

# Example usage
if __name__ == '__main__':
    # Step 1: Generate the ticker.txt file containing S&P 500 CIKs
    generate_ticker_file()  # This will download the CIKs for S&P 500 companies

    # Step 2: Read S&P 500 CIKs from the generated ticker.txt
    sp500_ciks = read_sp500_ciks('ticker.txt')

    # Step 3: Set the master index file (generated by EDGAR_Pac.py)
    master_index_file = 'master_index.csv'  # The consolidated master index from EDGAR_Pac

    # Step 4: Download 10-Q forms for the past 5 years (2018-2022)
    total_filings = download_sp500_forms(master_index_file, sp500_ciks, start_year=2018, end_year=2022)

    print(f"Expected to download approximately 10,000 filings. Downloaded: {total_filings}")

    # Step 5: Check the total number of downloaded files in the 'downloads' folder
    total_downloaded = check_downloaded_files()

    print(f"Final number of downloaded files: {total_downloaded}")
