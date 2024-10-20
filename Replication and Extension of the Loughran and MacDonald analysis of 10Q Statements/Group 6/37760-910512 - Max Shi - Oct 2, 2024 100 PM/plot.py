import pandas as pd
import matplotlib.pyplot as plt

file_path = r'C:\Users\max20\Downloads\NLP\10Q_TFIDF_ExcessReturns.csv'
df = pd.read_csv(file_path)

# Segregate TF-IDF into quintiles
df['TF-IDF Quintile'] = pd.qcut(df['TF-IDF'], 5, labels=False)

# Calculate the average excess returns for each quintile (3D and 4D)
average_returns = df.groupby('TF-IDF Quintile').agg({
    'Excess Return 3D': 'mean',
    'Excess Return 4D': 'mean'
}).reset_index()

# Plot the average excess returns for each TF-IDF quintile
plt.figure(figsize=(10, 6))

plt.plot(average_returns['TF-IDF Quintile'], average_returns['Excess Return 3D'], label='3-Day Excess Return', marker='o')
plt.plot(average_returns['TF-IDF Quintile'], average_returns['Excess Return 4D'], label='4-Day Excess Return', marker='s')

plt.title('Average Excess Returns by TF-IDF Quintiles')
plt.xlabel('TF-IDF Quintiles')
plt.ylabel('Average Excess Return')
plt.legend()
plt.grid(True)

plt.show()
