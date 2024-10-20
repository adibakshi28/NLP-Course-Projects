import csv
import re
import os
from collections import Counter
import numpy as np


def load_master_dictionary(file_path):
    dictionary = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['Word'].upper()
            dictionary[word] = {
                'Sequence Number': row['Sequence Number'],
                'Word Count': row['Word Count'],
                'Negative': row['Negative'],
                'Positive': row['Positive'],
            }
    return dictionary


def clean_text(text):
    # 移除尖括号中的内容
    text = re.sub(r'<.*?>', '', text)
    # 移除非字母数字字符
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text


def count_word_frequencies(text, lm_dictionary):
    cleaned_text = clean_text(text).upper()
    words = cleaned_text.split()

    word_count = Counter(words)
    frequencies = {word: word_count[word] for word in lm_dictionary if word in word_count}

    return frequencies


def process_all_files_in_directory(lm_dictionary, cleaned_dir):
    # Initialize variables
    word_list = [word for word in lm_dictionary]
    num_docs = len([f for f in os.listdir(cleaned_dir) if f.endswith('.txt')])
    num_words = len(word_list)

    # Create empty matrices
    tf_matrix = np.zeros((num_docs, num_words))
    idf_matrix = np.zeros((num_docs, num_words))
    doc_length_matrix = np.zeros((num_docs, 1))

    doc_index = 0

    # Process each file in the directory
    for filename in os.listdir(cleaned_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(cleaned_dir, filename)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                mda_content = f.read()

            word_frequencies = count_word_frequencies(mda_content, lm_dictionary)
            total_words = sum(word_frequencies.values())

            # Update document length matrix
            doc_length_matrix[doc_index, 0] = total_words

            # Update tf and idf matrices
            for word, freq in word_frequencies.items():
                word_index = word_list.index(word)
                tf_matrix[doc_index, word_index] = freq
                idf_matrix[doc_index, word_index] = 1  # The word appeared in this document

            doc_index += 1
            print(doc_index)
    # Calculate IDF (log(N / (1 + df)))
    doc_freq = np.sum(idf_matrix, axis=0)
    idf_values = np.log(num_docs / (1 + doc_freq))

    # Apply IDF to the tf matrix to get tf-idf
    tfidf_matrix = tf_matrix * idf_values


    return tfidf_matrix, doc_length_matrix, tf_matrix, idf_matrix


def calculate_tfidf_weight(tf_matrix, idf_matrix, doc_length_matrix):
    # Prevent division by zero
    epsilon = 0.01  # value to avoid division by zero
    safe_doc_length = np.where(doc_length_matrix == 0, epsilon, doc_length_matrix)

    # Normalize tf by document length
    term_weight = tf_matrix / safe_doc_length

    return term_weight


# Load the dictionary
lm_dictionary = load_master_dictionary('LoughranMcDonald_MasterDictionary_2018.csv')

# Specify directories
cleaned_dir = './cleaned'

# Process files and get matrices
tfidf_matrix, doc_length_matrix, tf_matrix, idf_matrix = process_all_files_in_directory(lm_dictionary, cleaned_dir)

# Calculate term weights
term_weight = calculate_tfidf_weight(tf_matrix, idf_matrix, doc_length_matrix)

import os
import numpy as np


output_dir = './matrix'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


np.save(os.path.join(output_dir, 'tfidf_matrix.npy'), tfidf_matrix)
np.save(os.path.join(output_dir, 'term_weight.npy'), term_weight)
np.save(os.path.join(output_dir, 'doc_length_matrix.npy'), doc_length_matrix)
np.save(os.path.join(output_dir, 'tf_matrix.npy'), tf_matrix)  #  tf_matrix
np.save(os.path.join(output_dir, 'idf_matrix.npy'), idf_matrix)  #  idf_matrix
