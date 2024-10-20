import csv
import glob
import re
import string
import sys
import time
import Load_MasterDictionary as LM
import numpy as np

# User defined directory for files to be parsed
TARGET_FILES = r'D:/python_working_fold/7871NLP/hw1/TestParse/*.*'
# User defined file pointer to LM dictionary
MASTER_DICTIONARY_FILE = r'D:/python_working_fold/7871NLP/hw1/Dictionary' + \
                         '/LoughranMcDonald_MasterDictionary_2018.csv'
# User defined output file
OUTPUT_FILE_doc_len = r'D:/python_working_fold/7871NLP/hw1/output/doc_len.csv'
OUTPUT_FIELDS_doc_len = ['file name', 'number of words']

OUTPUT_FILE_tf = r'D:/python_working_fold/7871NLP/hw1/output/tf.csv'
OUTPUT_FILE_idf = r'D:/python_working_fold/7871NLP/hw1/output/idf.csv'

lm_dictionary = LM.load_masterdictionary(MASTER_DICTIONARY_FILE, True)
fin_neg_list = LM.load_fin_neg_list(MASTER_DICTIONARY_FILE)
fin_neg_set = set(fin_neg_list)
fin_neg_order = {value: index for index, value in enumerate(fin_neg_list)}

OUTPUT_FIELDS_tf = ['file name'] + fin_neg_list
OUTPUT_FIELDS_idf = ['file name'] + fin_neg_list


root_dir = r"D:\python_working_fold\7871NLP\hw1\data"
years = [f"{year}" for year in range(2019, 2024)]  # ['2019', '2020', '2021', '2022', '2023']
quarters = [f"QTR{i}" for i in range(1, 5)]  # ['QTR1', 'QTR2', 'QTR3', 'QTR4']
FILE_PATHS = []
for year in years:
    for quarter in quarters:
        pattern = root_dir + f"\{year}\{quarter}\*"
        FILE_PATHS.extend(glob.glob(pattern))


def get_data(doc):
    word_num = 0
    tf_vector = [0] * len(fin_neg_list)
    idf_vector = [0] * len(fin_neg_list)
    
    tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
    for token in tokens:
        if not token.isdigit() and len(token) > 1 and token in lm_dictionary:
            word_num += 1  # word count
            if token in fin_neg_order:
                tf_vector[fin_neg_order[token]] += 1
                idf_vector[fin_neg_order[token]] = 1
        
    return word_num, tf_vector, idf_vector


def main():
    f_out_doc_len = open(OUTPUT_FILE_doc_len, 'w')
    wr_doc_len = csv.writer(f_out_doc_len, lineterminator='\n')
    wr_doc_len.writerow(OUTPUT_FIELDS_doc_len)

    f_out_tf = open(OUTPUT_FILE_tf, 'w')
    wr_tf = csv.writer(f_out_tf, lineterminator='\n')
    wr_tf.writerow(OUTPUT_FIELDS_tf)

    f_out_idf = open(OUTPUT_FILE_idf, 'w')
    wr_idf = csv.writer(f_out_idf, lineterminator='\n')
    wr_idf.writerow(OUTPUT_FIELDS_idf)

    #file_list = glob.glob(TARGET_FILES)
    file_list = TARGET_FILES
    print(file_list)
    for file in file_list:
        print(file)
        with open(file, 'r', encoding='UTF-8', errors='ignore') as f_in:
            doc = f_in.read()
        doc = re.sub('(May|MAY)', ' ', doc)  # drop all May month references
        doc = doc.upper()  # for this parse caps aren't informative so shift

        # calculate the values of output matrix
        output, tf_row, idf_row = get_data(doc)

        # populate the matrix doc_len
        doc_len_data = [0] * 2
        doc_len_data[0] = file
        doc_len_data[1] = output
        wr_doc_len.writerow(doc_len_data)

        # populate the matrix tf
        wr_tf.writerow([file] + tf_row)

        # populate the matric idf
        wr_idf.writerow([file] + idf_row)


if __name__ == '__main__':
    print('\n' + time.strftime('%c') + '\ntfidf_calculation.py\n')
    main()
    import pandas as pd
    doc_len_df = pd.read_csv(OUTPUT_FILE_doc_len, index_col=0)
    doc_len_series = doc_len_df['number of words']
    tf_df = pd.read_csv(OUTPUT_FILE_tf, index_col=0)
    idf_df = pd.read_csv(OUTPUT_FILE_idf, index_col=0)
    N = len(doc_len_df)
    df_series = idf_df.sum()
    tf_idf_df = pd.DataFrame(0.0, index=tf_df.index, columns=tf_df.columns)

    for i in range(len(fin_neg_list)):  # the i_th word
        for j in range(N):  # the j_th document 
            if tf_df.iloc[j,i] >= 1:
                value = ((1 + np.log(tf_df.iloc[j,i])) / (1 + np.log(doc_len_series.iloc[j]))) * (np.log(N/df_series.iloc[i]))
                tf_idf_df.iloc[j,i] = value
    tf_idf_df.to_csv("tfidf_matrix.csv")
    neg_freq = tf_df.sum(axis=1)
    neg_portion = neg_freq/doc_len_series
    neg_portion.to_csv("neg_portion.csv")
    weighted_neg_freq = (tf_df * tf_idf_df).sum(axis=1)
    weighted_neg_portion = weighted_neg_freq/doc_len_series
    weighted_neg_portion.to_csv("weighted_neg_portion.csv")
    print('\n' + time.strftime('%c') + '\nNormal termination.')