import os
import pandas as pd
from collections import Counter

# Load words from the CSV file
words_df = pd.read_csv('Harvard_Negative_Words_List.txt', header=None)  # Assuming the words are in the first column
# words_list = words_df.iloc[:, 0].tolist()
# Ensure all words are strings and handle missing values
words_list = words_df.iloc[:, 0].fillna('').astype(str).tolist() # Get the list of words from the first column

# Create an empty dictionary to store word counts for each file
word_counts = {word: [] for word in words_list}

# Folder path containing the .txt files
# folder_path = 'tiny_10Qtxt'
folder_path = 'sec_parser_subset'

# Get list of .txt files in the folder
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# Process each .txt file in the folder
for txt_file in txt_files:
    # Read the content of the text file
    with open(os.path.join(folder_path, txt_file), 'r', encoding='utf-8') as file:
        text = file.read().lower()  # Convert text to lowercase for case-insensitive matching

    # Count occurrences of each word
    word_counter = Counter(text.split())

    # Append the count of each word to the corresponding list in word_counts
    for word in words_list:
        word_counts[word].append(word_counter.get(word.lower(), 0))  # Use .get to handle missing words

# Convert the word_counts dictionary to a DataFrame
count_matrix_df = pd.DataFrame(word_counts, index=txt_files)

# Save the result to a CSV file
count_matrix_df.to_csv('word_count_matrix.csv')

# Load file stats from the CSV file
# stats_df = pd.read_csv('Parser.csv')
stats_df = pd.read_csv('Parser.csv')
stats_df.head()

import warnings

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

import math

df_tf_idf = count_matrix_df.copy()
df_i=[0] * count_matrix_df.shape[1]

for i in range(df_tf_idf.shape[0]):#docs
    for j in range(df_tf_idf.shape[1]):## words
        if(df_tf_idf.iloc[i,j]):
            df_tf_idf.iloc[i,j]=(1+math.log(df_tf_idf.iloc[i,j]))/(1+math.log(stats_df['number of words,'][i]))
            df_i[j]+=1

df_i=[math.log(df_tf_idf.shape[0]/i) if i else i for i in df_i]
df_tf_idf = df_tf_idf.mul(df_i, axis=1)
df_=df_tf_idf.copy()

print(df_.head(5))

print(df_.shape)



### weighting
# Multiply the weights by the counts for each row (element-wise multiplication)
weighted_counts = df_ * count_matrix_df

# Sum the weighted counts for each row to get the total weighted negative words per document
weighted_sum = weighted_counts.sum(axis=1)

# Create a new DataFrame to store the result, keeping the same index as the original dataframes
weighted_sum_df = pd.DataFrame(weighted_sum, columns=['Weighted_Negative_Sum'])

# Display the new dataframe
print(weighted_sum_df.head())

# prepping up df for the excess returns
# Function to extract CIK and date from the index
def extract_cik_and_date(index):
    # Split the index string by underscore
    parts = index.split('_')
    # Extract the CIK (first part)
    cik = parts[0]
    # Extract the date (second part)
    date = parts[1]
    return cik, date

# Apply the function to extract CIK and date
weighted_sum_df['CIK'] = weighted_sum_df.index.map(lambda x: extract_cik_and_date(x)[0])
weighted_sum_df['Release_Date'] = weighted_sum_df.index.map(lambda x: extract_cik_and_date(x)[1])

# Display the updated dataframe with new columns
print(weighted_sum_df.head())


### excess returns
### computing excess returns
import pandas as pd

# Load the CSV file (assuming it's stored locally as "sp500_closing_prices.csv")
file_path = 'sp500_closing_prices.csv'  # Adjust the file path as needed
sp500_closing_prices = pd.read_csv(file_path)

# Ensure 'Date' is treated as the index
sp500_closing_prices.set_index('Date', inplace=True)

# Convert all columns to numeric, forcing any errors to NaN
sp500_closing_prices = sp500_closing_prices.apply(pd.to_numeric, errors='coerce')

# Calculate the returns for each stock (and the SP500 index)
returns = sp500_closing_prices.pct_change()

# Compute the excess returns (returns of each stock minus the SP500 returns)
excess_returns = returns.subtract(returns['^GSPC'], axis=0)
excess_returns.to_csv("excess_returns.csv")

# Display the first few rows of excess returns
print(excess_returns.head())





### changing the column names from tickers to CIK
# Load the excess_returns and sp500_ciks data
excess_returns_file_path = 'excess_returns.csv'  # Path to your excess returns data
sp500_ciks_file_path = 'sp500_ciks.csv'  # Path to the SP500 CIKs CSV

# Assuming you already have excess_returns dataframe loaded, here we'll focus on renaming the columns
excess_returns = pd.read_csv(excess_returns_file_path)  # Adjust this if already loaded
sp500_ciks_df = pd.read_csv(sp500_ciks_file_path)

# Ensure 'Date' is treated as the index
excess_returns.set_index('Date', inplace=True)

# Ensure the CIK column is treated as a string (with leading zeros)
sp500_ciks_df['CIK'] = sp500_ciks_df['CIK'].astype(str).str.zfill(10)

# Create a dictionary mapping from Ticker to CIK, ensuring leading zeros are preserved
ticker_to_cik = dict(zip(sp500_ciks_df['Ticker'], sp500_ciks_df['CIK']))

# Replace the column names in excess_returns with CIK numbers, keeping original names for unmatched columns
new_columns = [ticker_to_cik.get(col, col) for col in excess_returns.columns]
excess_returns.columns = new_columns

# Save the updated excess_returns to a new file (optional)
excess_returns.to_csv('updated_excess_returns.csv', index=False)

print(excess_returns.head())


###### real plotting
import pandas as pd
import matplotlib.pyplot as plt

# Assume excess_returns is a DataFrame with CIKs as columns and dates as index
# excess_returns = pd.read_csv('excess_returns.csv', index_col='date', parse_dates=True)

# Iterate over weighted_sum_df and calculate total 4-day, 3-day, and 2-day excess returns
for idx, row in weighted_sum_df.iterrows():
    cik = row['CIK']
    release_date = row['Release_Date']
    
    # Ensure release_date is valid or find the next closest valid date in excess_returns
    try:
        closest_idx = excess_returns.index.searchsorted(release_date)
        
        # Make sure closest_idx is within bounds and extract the proper data slice
        if closest_idx < len(excess_returns):
            closest_date = excess_returns.index[closest_idx]
            
            # Get the 4-day range (from the closest release_date + 4 days)
            excess_return_4_days = excess_returns.loc[closest_date:closest_date].iloc[:5][cik].sum()
            
            # Ensure excess_return_4_days is a scalar (not a Series or DataFrame)
            if isinstance(excess_return_4_days, (int, float)):
                weighted_sum_df.at[idx, '4_day_excess_return'] = excess_return_4_days
            else:
                weighted_sum_df.at[idx, '4_day_excess_return'] = 0  # Set to 0 if not a scalar

            # Handle the 3-day excess return
            excess_return_3_days = excess_returns.loc[closest_date:closest_date].iloc[:4][cik].sum()
            if isinstance(excess_return_3_days, (int, float)):
                weighted_sum_df.at[idx, '3_day_excess_return'] = excess_return_3_days
            else:
                weighted_sum_df.at[idx, '3_day_excess_return'] = 0

            # Handle the 2-day excess return
            excess_return_2_days = excess_returns.loc[closest_date:closest_date].iloc[:3][cik].sum()
            if isinstance(excess_return_2_days, (int, float)):
                weighted_sum_df.at[idx, '2_day_excess_return'] = excess_return_2_days
            else:
                weighted_sum_df.at[idx, '2_day_excess_return'] = 0

    except (KeyError, IndexError):
        # Handle cases where date is out of bounds or no valid CIK
        weighted_sum_df.at[idx, '4_day_excess_return'] = 0
        weighted_sum_df.at[idx, '3_day_excess_return'] = 0
        weighted_sum_df.at[idx, '2_day_excess_return'] = 0

import pandas as pd
import matplotlib.pyplot as plt

# Assuming `weighted_sum_df` is your final DataFrame with the 'Weighted_Negative_Sum' and excess returns columns

# Plot only non-zero 4-day excess returns
non_zero_4day = weighted_sum_df[weighted_sum_df['4_day_excess_return'] != 0]

# Flip axes and color code based on positive/negative return
plt.figure(figsize=(8,6))
colors_4day = ['green' if val > 0 else 'red' for val in non_zero_4day['4_day_excess_return']]
plt.scatter(non_zero_4day['Weighted_Negative_Sum'], non_zero_4day['4_day_excess_return'], c=colors_4day)
plt.xlabel('Weighted Negative Sum')
plt.ylabel('4-Day Excess Return')
plt.title('4-Day Excess Return vs Weighted Negative Sum')
plt.axhline(0, color='black', linestyle='--')  # Add a horizontal line at y=0
plt.show()

# Plot only non-zero 3-day excess returns
non_zero_3day = weighted_sum_df[weighted_sum_df['3_day_excess_return'] != 0]

# Flip axes and color code based on positive/negative return
plt.figure(figsize=(8,6))
colors_3day = ['green' if val > 0 else 'red' for val in non_zero_3day['3_day_excess_return']]
plt.scatter(non_zero_3day['Weighted_Negative_Sum'], non_zero_3day['3_day_excess_return'], c=colors_3day)
plt.xlabel('Weighted Negative Sum')
plt.ylabel('3-Day Excess Return')
plt.title('3-Day Excess Return vs Weighted Negative Sum')
plt.axhline(0, color='black', linestyle='--')  # Add a horizontal line at y=0
plt.show()

# Create quintiles based on the 'Weighted_Negative_Sum' column
# Drop rows with zero 4-day excess return
non_zero_weighted_df = weighted_sum_df[weighted_sum_df['4_day_excess_return'] != 0]

# Create quintiles based on the 'Weighted_Negative_Sum' column
non_zero_weighted_df['negative_quintile'] = pd.qcut(non_zero_weighted_df['Weighted_Negative_Sum'], 5, labels=["Low", "2", "3", "4", "High"])

# Calculate the median 4-day excess return for each quintile
median_excess_return_by_quintile = non_zero_weighted_df.groupby('negative_quintile')['4_day_excess_return'].median()

# Plot the median 4-day excess return for each quintile
plt.figure(figsize=(8, 6))
plt.plot(median_excess_return_by_quintile.index, median_excess_return_by_quintile.values, marker='o', linestyle='-', color='black', label='Median 4-Day Excess Return')

# Customize the plot with increased granularity
plt.xlabel('Quintile (based on Weighted Negative Sum)')
plt.ylabel('Median 4-Day Excess Return')
plt.title('Median 4-Day Excess Return Across Weighted Negative Sum Quintiles')
plt.grid(True, linestyle='--', linewidth=0.5)

# Zoom into the y-axis to show more detailed variations
y_min = median_excess_return_by_quintile.min() - 0.001  # Small offset for better view
y_max = median_excess_return_by_quintile.max() + 0.001
plt.ylim(y_min, y_max)

# Increase precision on y-axis labels
plt.yticks([round(x, 4) for x in plt.yticks()[0]])

# Display the plot
plt.show()

### Mean Calculation:
# Drop rows with zero 4-day excess return
non_zero_weighted_df = weighted_sum_df[weighted_sum_df['4_day_excess_return'] != 0]

# Create quintiles based on the 'Weighted_Negative_Sum' column
non_zero_weighted_df['negative_quintile'] = pd.qcut(non_zero_weighted_df['Weighted_Negative_Sum'], 5, labels=["Low", "2", "3", "4", "High"])

# Calculate the mean 4-day excess return for each quintile (replacing median with mean)
mean_excess_return_by_quintile = non_zero_weighted_df.groupby('negative_quintile')['4_day_excess_return'].mean()

# Plot the mean 4-day excess return for each quintile
plt.figure(figsize=(8, 6))
plt.plot(mean_excess_return_by_quintile.index, mean_excess_return_by_quintile.values, marker='o', linestyle='-', color='black', label='Mean 4-Day Excess Return')

# Customize the plot with increased granularity
plt.xlabel('Quintile (based on Weighted Negative Sum)')
plt.ylabel('Mean 4-Day Excess Return')
plt.title('Mean 4-Day Excess Return Across Weighted Negative Sum Quintiles')
plt.grid(True, linestyle='--', linewidth=0.5)

# Zoom into the y-axis to show more detailed variations
y_min = mean_excess_return_by_quintile.min() - 0.001  # Small offset for better view
y_max = mean_excess_return_by_quintile.max() + 0.001
plt.ylim(y_min, y_max)

# Increase precision on y-axis labels
plt.yticks([round(x, 4) for x in plt.yticks()[0]])

# Display the plot
plt.show()
