import os
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

# Load the tokenizer, model, and config from the FOMC-RoBERTa model
tokenizer = AutoTokenizer.from_pretrained("gtfintechlab/FOMC-RoBERTa", do_lower_case=True, do_basic_tokenize=True)
model = AutoModelForSequenceClassification.from_pretrained("gtfintechlab/FOMC-RoBERTa", num_labels=3)
config = AutoConfig.from_pretrained("gtfintechlab/FOMC-RoBERTa")

# Create a classifier pipeline for text classification
classifier = pipeline('text-classification', model=model, tokenizer=tokenizer, config=config, device=0, framework="pt")

def get_file_names(file_type):
    """
    Get the list of CSV file names from the filtered directory for the specified file type.
    """
    dir_path = f'./data/{file_type}_filtered'
    entries = os.listdir(dir_path)
    file_names = [entry for entry in entries if entry.endswith('.csv') and os.path.isfile(os.path.join(dir_path, entry))]
    return file_names

def main():
    # Define the types of FOMC data to process
    #file_types = ['FOMC_Minutes', 'FOMC_Presconf', 'FOMC_Speech']
    file_types = ['FOMC_Minutes']
    # Create an empty DataFrame to store the results
    results_df = pd.DataFrame(columns=['File Name', 'File Type', 'Date', 'Number of Sentences', 'Sentiment Index'])
    
    for file_type in file_types:
        # Get the list of files for the current file type
        file_names = get_file_names(file_type)
        
        for file_name in file_names:
            file_path = f'./data/{file_type}_filtered/' + file_name
            data = pd.read_csv(file_path, header=None, names=['text'])
            total_sentences = len(data)  # Total number of sentences
            
            # Initialize counters for hawkish and dovish sentiments
            hawkish_count = 0
            dovish_count = 0

            # Iterate over each row (sentence) in the CSV file
            for _, row in data.iterrows():
                text = row['text']  # Extract the sentence text
                # Perform sentiment classification using the model
                results = classifier(text, batch_size=128, truncation="only_first")
                
                # Update sentiment counters based on classification result
                if results[0]['label'] == 'LABEL_1':  # Hawkish
                    hawkish_count += 1
                elif results[0]['label'] == 'LABEL_0':  # Dovish
                    dovish_count += 1

            # Calculate the sentiment index
            if total_sentences > 0:
                sentiment_index = (hawkish_count - dovish_count) / total_sentences
            else:
                sentiment_index = 0  # If no valid sentences, sentiment index is 0

            # Extract the date from the file name
            if file_type == 'FOMC_Speech':
                date = file_name[-13:-5]
            else:
                date = file_name[-12:-4]

            # Create a new row for the current file's results
            new_row = pd.DataFrame({
                'File Name': [file_name[:-4]],  # File name without extension
                'File Type': [file_type],
                'Date': [date], 
                'Number of Sentences': [total_sentences],
                'Sentiment Index': [sentiment_index]
            })

            # Add the new row to the results DataFrame
            results_df = pd.concat([results_df, new_row], ignore_index=True)

    # Print the final results DataFrame
    print(results_df)
    results_df.to_csv('./data/FOMC_RoBERTa_sentiment_index1.csv', index=False)

if __name__ == '__main__':
    main()
