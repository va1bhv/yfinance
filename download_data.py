import pandas as pd
import streamlit
import yfinance as yf


@streamlit.cache_data
def download_data(tickers, collection_period: int, collection_interval: int):
    raw_data: pd.DataFrame = yf.download(tickers,
                                         period=collection_period,
                                         interval=collection_interval,
                                         group_by='ticker',
                                         threads=True,
                                         progress=False)
    # raw_data.reset_index(drop=False, inplace=True, names='DateTime')
    return raw_data
