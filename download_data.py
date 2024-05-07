import collections

import pandas as pd
import yfinance as yf


def download_data(tickers: collections.Iterable, collection_period: int, collection_interval: int):
    raw_data: pd.DataFrame = yf.download(tickers,
                                         period=collection_period,
                                         interval=collection_interval,
                                         group_by='ticker',
                                         threads=True)
    raw_data.reset_index(drop=False, inplace=True, names='DateTime')
