import pandas as pd
from tqdm import tqdm

tqdm.pandas()


def read_data(top_n: int) -> pd.DataFrame:
    tickers = pd.read_excel("MCAP28032024.xlsx")
    tickers = tickers.drop(columns=['Sr. No.'])
    tickers.rename(columns={'Market capitalization as on March 28, 2024\n(In lakhs)': 'Market Cap'}, inplace=True)
    tickers['Symbol'] = tickers['Symbol'] + '.NS'
    tickers[['Close to crossover', 'Close', 'MA5', 'MA20', 'Next Diff %', 'RSI']] = False
    tickers.set_index('Symbol', drop=False, inplace=True)
    tickers_top_n = tickers.nlargest(top_n, 'Market Cap')
    return tickers_top_n
