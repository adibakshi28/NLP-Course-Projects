import os
import re
from tqdm import tqdm
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from finbert_embedding.embedding import FinbertEmbedding
finbert = FinbertEmbedding()


# read csv file into a list
def read_csv(file_path):
    """
    read csv file into a list
    """
    try:
        df = pd.read_csv(file_path, header=None)
        # check whether there is valid sentence in the file
        if df.empty:
            return []
        return df[0].tolist()
    except pd.errors.EmptyDataError:
        return []


# calculate cosine distance
def cosine_similarity_between_vectors(vec1, vec2):
    """
    calculate cosine distance
    """
    return cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]


# calculate inf score and int score
def compute_individual_averages(csv_file, finbert):
    """
    calculate inf score and int score
    """
    # target sentences
    interest_sentence = "Interest rates will rise"
    inflation_sentence = "Inflation will rise"
    # load sentences
    sentences = read_csv(csv_file)
    # calculate target sentence vector
    target_interest_vector = finbert.sentence_vector(interest_sentence)
    target_inflation_vector = finbert.sentence_vector(inflation_sentence)
    # create containers to store the int score and inf score of all the sentences in the file
    interest_similarities = []
    inflation_similarities = []
    
    for sentence in sentences:
        sentence_vector = finbert.sentence_vector(sentence)
        # calculate interest similarity
        similarity_with_interest = cosine_similarity_between_vectors(sentence_vector, target_interest_vector)
        interest_similarities.append(similarity_with_interest)
        # alculate inflation similarity
        similarity_with_inflation = cosine_similarity_between_vectors(sentence_vector, target_inflation_vector)
        inflation_similarities.append(similarity_with_inflation)
    # calculate int score and inf score
    interest_avg_similarity = np.mean(interest_similarities)
    inflation_avg_similarity = np.mean(inflation_similarities)
    
    return interest_avg_similarity, inflation_avg_similarity


# extract date from file name
def extract_date_from_filename(filename):
    """
    extract date from file name
    """
    # extract date from file name by re
    match = re.search(r'(\d{8})', filename)
    if match:
        date_str = match.group(1)
        return pd.to_datetime(date_str, format='%Y%m%d')
    return None


# calculate the result of all the files in the folder path
def process_folder(folder_path, finbert):
    """
    calculate the result of all the files in the folder path
    """
    results = []
    # get all the csv files
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    # utilize tqdm to show the process
    for filename in tqdm(csv_files, desc="Processing files", unit="file"):
        file_path = os.path.join(folder_path, filename)
        sentences = read_csv(file_path)
        if not sentences:
            # skip if there is no vaid sentence in the file
            continue
        # calculate int score and inf score for each file
        interest_avg, inflation_avg = compute_individual_averages(file_path, finbert)
        # extract date from file name
        file_date = extract_date_from_filename(filename)
        # add the result to a list
        results.append({
            "date": file_date,
            "file": filename,
            "int score": interest_avg,
            "inf score": inflation_avg
        })
    df = pd.DataFrame(results)  # convert list to a DataFrame
    
    return df


if __name__ == '__main__':
    # calculation of factor similarity for FOMC Minutes
    folder_path = 'D:\\python_working_fold\\7871NLP\\hw2\\FOMC_Minutes_filtered'
    df = process_folder(folder_path, finbert)
    df.to_csv("DOMC_Minutes_factor_similarity.csv")

    # calculation of factor similarity for FOMC Speech
    folder_path = 'D:\\python_working_fold\\7871NLP\\hw2\\FOMC_Speech_filtered'
    df = process_folder(folder_path, finbert)
    df.to_csv("FOMC_Speech_factor_similarity.csv")

    # calculation of factor similarity for FOMC Press Conference
    folder_path = 'D:\\python_working_fold\\7871NLP\\hw2\\FOMC_Presconf_filtered'
    df = process_folder(folder_path, finbert)
    df.to_csv("FOMC_Presconf_factor_similarity.csv")