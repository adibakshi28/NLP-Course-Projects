import pandas as pd
import re
import statsmodels.api as sm
import wrds
import matplotlib.pyplot as plt

def process_weight_file(weight_df, cik_df):
    """Processes the weight file to add date, cik, and ticker."""
    weight_df['filingdate'] = weight_df['file name'].apply(extract_date)
    weight_df['cik'] = weight_df['file name'].apply(extract_cik)
    weight_df['ticker'] = weight_df['cik'].apply(lambda cik: extract_ticker(cik, cik_df))
    return weight_df

def extract_date(file_name):
    """Extracts the filing date from a file name."""
    date_part = file_name.split('\\')[-1][:8]
    return pd.to_datetime(date_part, format='%Y%m%d')

def extract_cik(file_name):
    """Extracts the CIK from a file name using regular expressions."""
    match = re.search(r'edgar_data_(\d+)_', file_name)
    if match:
        return match.group(1).zfill(10)  # Ensures CIK is 10 digits long
    return pd.NA
 
def extract_ticker(cik, cik_df):
    """Retrieves ticker from CIK."""
    ticker = cik_df[cik_df['CIK']==cik]['Ticker'].iloc[0]
    return ticker

def get_sp500_ret(db, start_date, end_date):
    """Fetches S&P 500 returns over a specified date range using SQL."""
    query = """
    SELECT date, ret
    FROM crsp.dsf
    WHERE permno IN (SELECT permno FROM crsp.stocknames WHERE ticker = 'SPY')
    AND date BETWEEN %(start_date)s AND %(end_date)s
    ORDER BY date
    """
    data = db.raw_sql(query, params={'start_date': start_date, 'end_date': end_date})
    data['date'] = pd.to_datetime(data['date'])
    data.rename(columns={'ret':'sp500_ret'},inplace=True)
    return data

def get_excess_ret(k, tfidf, trading_days, db, sp500_df):
    """Calculates excess returns for a given period k."""
    excess_ret_df = pd.DataFrame()
    for _, row in tfidf.iterrows():
        ticker = row['ticker']
        filingdate = pd.to_datetime(row['filingdate'])
        past_dates = trading_days[trading_days['date'] <= filingdate]
        future_dates = trading_days[trading_days['date'] > filingdate]
        
        if len(past_dates) >= 90 and len(future_dates) >= k:
            # Fetch past and future returns
            past_dates_to_fetch = past_dates.iloc[-90:]['date'].tolist()
            past_stock_data, past_sp500_data = fetch_rets(ticker, past_dates_to_fetch, db, sp500_df)
            future_dates_to_fetch = future_dates.iloc[:k]['date'].tolist()
            future_stock_data, future_sp500_data = fetch_rets(ticker, future_dates_to_fetch, db, sp500_df)
            
            if not past_stock_data.empty and not past_sp500_data.empty:
                excess_ret = calc_excess_ret(past_stock_data, past_sp500_data, future_stock_data, future_sp500_data)
                excess_ret_df = pd.concat([excess_ret_df, pd.DataFrame({
                    'ticker': [ticker], 'filingdate': [filingdate], 'excess_ret': [excess_ret]
                })], ignore_index=True)
    return excess_ret_df

def fetch_rets(ticker, dates, db, sp500_df):
    """Fetches stock and S&P 500 returns for specified dates."""
    stock_query = """
    SELECT date, ret as stock_ret
    FROM crsp.dsf
    WHERE permno IN (SELECT permno FROM crsp.stocknames WHERE ticker = %(ticker)s)
    AND date in %(dates)s
    """
    stock_data = db.raw_sql(stock_query, params={'ticker': ticker, 'dates': tuple(dates)})
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    sp500_data = sp500_df[sp500_df['date'].isin(dates)]
    return stock_data, sp500_data

def calc_excess_ret(past_stock_data, past_sp500_data, future_stock_data, future_sp500_data):
    """Calculates the excess return by regression and future prediction."""
    past_stock_df = pd.merge(past_stock_data, past_sp500_data, on=['date']).dropna()
    X = sm.add_constant(past_stock_df['sp500_ret'])
    model = sm.OLS(past_stock_df['stock_ret'], X).fit()
    future_stock_actual = ((1 + future_stock_data['stock_ret']).cumprod() - 1).iloc[-1]
    future_stock_pred = ((1 + model.predict(sm.add_constant(future_sp500_data['sp500_ret']))).cumprod() - 1).iloc[-1]
    return future_stock_actual - future_stock_pred

def analyze_by_weight(excess_ret_df, weight_df, weight_name, k):
    """Analyzes and plots excess returns by weight quintiles."""
    merged_data = pd.merge(excess_ret_df, weight_df, on=['filingdate', 'ticker'])
    merged_data['quintile'] = pd.qcut(merged_data['0'], 5, labels=False)
    quintile_means = merged_data.groupby('quintile')['excess_ret'].mean()

    plt.figure(figsize=(10, 6))
    plt.plot(quintile_means.index + 1, quintile_means.values, marker='o', linestyle='-', color='b')
    plt.title(f'Excess Returns by {weight_name.capitalize()} Quintile for {k} Days')
    plt.xlabel(f'{weight_name.capitalize()} Quintile')
    plt.ylabel('Average Excess Return')
    plt.grid(True)
    plt.xticks(range(1, 6))
    plt.savefig(f'output/Excess_Returns_by_{weight_name.capitalize()}_Quintile_{k}_Days.png')
    plt.show()

def main():
    # Establish connection to the WRDS database
    db = wrds.Connection()
    
    # Load datasets
    cik_df = pd.read_csv('./cik.csv')
    cik_df['CIK'] = cik_df['CIK'].astype(str).str.zfill(10)
    
    tfidf = pd.read_csv('./weighted_neg_portion.csv')
    term_weight = pd.read_csv('./neg_portion.csv')

    # Process weight files
    print("Processing weight file...")
    tfidf = process_weight_file(tfidf, cik_df)
    term_weight = process_weight_file(term_weight, cik_df)
    
    # Fetch sp500 data
    start_date = '2018-01-01'
    end_date = '2024-12-31'
    print("Fetching S&P 500 returns...")
    sp500_df = get_sp500_ret(db, start_date, end_date)
    trading_days = sp500_df[['date']]
    
    # Analysis
    period_lst = [3, 4]
    for k in period_lst:
        print(f"Processing for period: {k} days")
        excess_ret_df = get_excess_ret(k, tfidf, trading_days, db, sp500_df)
        analyze_by_weight(excess_ret_df, tfidf, 'tfidf', k)
        analyze_by_weight(excess_ret_df, term_weight, 'term_weight', k)

    # Close database connection
    db.close()

if __name__ == "__main__":
    main()
