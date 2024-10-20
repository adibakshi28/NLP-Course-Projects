# get all the urls for pdf files of FOMC minutes
def fetch_FOMCminutes_pdf_links(year, HISTORY_YEAR = 2018):
    """
    get all the urls for pdf files of FOMC minutes
    """
    import requests
    from bs4 import BeautifulSoup
    # HISTORY_YEAR = 2018
    # For files published before 2018, pdf files are stored in the history page
    if year <= HISTORY_YEAR:
        url = f'https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm'
        # url = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2017.htm"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        fomcminutes_links = []
        # Search for all the valid urls
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):  # search for pdf files
                full_url = f"https://www.federalreserve.gov{href}"
                last_part = href.split('/')[-1]
                if 'fomcminutes' in last_part:
                    fomcminutes_links.append(full_url)
    # For files published after 2018, pdf files are stored in the calendar page
    else: 
        url = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        fomcminutes_links = []
        # Search for all the valid urls
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):  # search for pdf files
                full_url = f"https://www.federalreserve.gov{href}"
                last_part = href.split('/')[-1]
                # extract file links in the year
                if 'fomcminutes'+str(year) in last_part:
                    fomcminutes_links.append(full_url)

    return fomcminutes_links


# download all the pdf files in the list
def download_pdfs(links, save_dir):
    """
    download all the pdf files in the list
    """
    import os
    import requests
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # down load all the pdf files based on the urls in the list
    for link in links:
        pdf_name = link.split('/')[-1]  # file name
        pdf_path = os.path.join(save_dir, pdf_name)  # file path
        response = requests.get(link)
        if response.status_code == 200:
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {pdf_name}")
        else:
            print(f"Failed to download: {pdf_name}, Status Code: {response.status_code}")


# download all the pdf files of FOMC minutes
def download_FOMCminutes(year_start, year_end):
    """
    download all the pdf files of FOMC minutes
    """
    # traverse all the years
    for year in range(year_start, year_end+1):
        # extract all the links of this year
        fomcminutes_links = fetch_FOMCminutes_pdf_links(year)
        # download all the files of this year
        download_pdfs(fomcminutes_links, "FOMC_Minutes")


# get all the urls for pdf files of FOMC press conference transcripts
def fetch_FOMCpresconf_pdf_links(year, HISTORY_YEAR=2018):
    """
    get all the urls for pdf files of FOMC press conference transcripts
    """
    import requests
    from bs4 import BeautifulSoup
    fomcpresconf_pdf_links = []
    # For files published before 2018, pdf files are stored in the history page
    if year <= HISTORY_YEAR:
        url = f'https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Search for all the valid urls
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Relative Path or Absolute Path
            if href.startswith('/'):
                full_url = f"https://www.federalreserve.gov{href}"
            else:
                full_url = href 

            last_part = href.split('/')[-1]
            # check the valid format for FOMC press conference transcripts
            if 'fomcpresconf' in last_part:
                # create urls for pdf files
                pdf_link = f"https://www.federalreserve.gov/mediacenter/files/{last_part.replace('.htm', '.pdf')}"
                fomcpresconf_pdf_links.append(pdf_link)
    # For files published after 2018, pdf files are stored in the calendar page
    else:
        url = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Search for all the valid urls
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Relative Path or Absolute Path
            if href.startswith('/'):
                full_url = f"https://www.federalreserve.gov{href}"
            else:
                full_url = href

            last_part = href.split('/')[-1]
            # extract file links in the year
            if 'fomcpresconf' in last_part and str(year) in last_part:
                pdf_link = f"https://www.federalreserve.gov/mediacenter/files/{last_part.replace('.htm', '.pdf')}"
                fomcpresconf_pdf_links.append(pdf_link)

    return fomcpresconf_pdf_links


# down load all the pdf files of FOMC press conference transcripts
def download_FOMCpresconf(year_start, year_end):
    """
    down load all the pdf files of FOMC press conference transcripts
    """
    # traverse all the years
    for year in range(year_start, year_end+1):
        # extract all the links of this year
        fomcpresconf_links = fetch_FOMCpresconf_pdf_links(year)
        # download all the files of this year
        download_pdfs(fomcpresconf_links, "FOMC_Presconf")


# get all the urls for pdf files of FOMC speeches
def fetch_FOMCspeech_pdf_links(year):
    """
    get all the urls for pdf files of FOMC speeches
    """
    import requests
    from bs4 import BeautifulSoup
    url = f'https://www.federalreserve.gov/newsevents/speech/{year}-speeches.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    speech_pdf_links = []

    # Search for all the valid urls
    for link in soup.find_all('a', href=True):
        href = link['href']
        # check the format of all the urls
        if href.startswith('/newsevents/speech') and href.endswith('.htm'):
            last_part = href.split('/')[-1]
            # extract speech links in the year
            if str(year) in last_part:
                # create urls for pdf files
                pdf_link = f"https://www.federalreserve.gov/newsevents/speech/files/{last_part.replace('.htm', '.pdf')}"
                speech_pdf_links.append(pdf_link)

    return speech_pdf_links


# down load all the pdf files of FOMC press speeches
def download_FOMCspeech(year_start, year_end):
    """
    down load all the pdf files of FOMC press speeches
    """
    # traverse all the years
    for year in range(year_start, year_end+1):
        # extract all the links of this year
        fomcpresconf_links = fetch_FOMCspeech_pdf_links(year)
        # download all the files of this year
        download_pdfs(fomcpresconf_links, "FOMC_Speech")


if __name__ == '__main__':
    download_FOMCminutes(2012, 2024)
    download_FOMCpresconf(2012, 2024)
    download_FOMCspeech(2012, 2024)