import warnings

import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm

tqdm.pandas()
warnings.filterwarnings("ignore")


# Check when crossover point is close and when MA5 is about to overtake MA20
# Check when the diff is going -ve to +ve
# Diff = MA5 - MA20
# When Diff is -ve and slope is +ve


def _get_data(tkr: str, rolling_up: int, rolling_down: int, raw_data: pd.DataFrame) -> pd.DataFrame:
    dt = raw_data[tkr]
    dt['MA5'] = dt['Close'].rolling(rolling_down).mean()
    dt['MA20'] = dt['Close'].rolling(rolling_up).mean()
    dt['%Diff'] = ((dt['MA5'] - dt['MA20']) / dt['MA5']) * 100
    dt.dropna(inplace=True)
    return dt


def _rsi(dta, window=14, adjust=False) -> float:
    delta = dta['Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    rs = gain_ewm / loss_ewm
    rsi_ans = 100 - 100 / (1 + rs)

    try:
        return rsi_ans.values[-1]
    except IndexError:
        return -1


def compute(tkr: str, rolling_up, rolling_down, width, tolerance, raw_data: pd.DataFrame) -> \
        tuple[bool, float, float, float, float, float]:
    temp = _get_data(tkr, rolling_up, rolling_down, raw_data)

    if temp.empty:
        return False, -1, -1, -1, -1, -1

    temp.reset_index(inplace=True, names='DateTime')
    time_series = temp['%Diff'].values
    close: float = temp['Close'].values[-1]
    ma5: float = temp['MA5'].values[-1]
    ma20: float = temp['MA20'].values[-1]

    if temp.empty:
        return False, close, ma5, ma20, -1, -1

    if len([i for i in time_series[-width:] > 0 if i]) > tolerance:
        return False, close, ma5, ma20, -1, -1

    nn = ARIMA(time_series, order=(1, 1, 0)).fit().forecast(steps=1)[0]
    if nn < 0:
        return False, close, ma5, ma20, nn, -1

    return True, close, ma5, ma20, nn, _rsi(temp)


def main() -> None:
    tickers = pd.read_excel("MCAP28032024.xlsx")
    tickers = tickers.drop(columns=['Sr. No.'])
    tickers.rename(columns={'Market capitalization as on March 28, 2024\n(In lakhs)': 'Market Cap'}, inplace=True)
    tickers['Symbol'] = tickers['Symbol'] + '.NS'
    tickers[['Close to crossover', 'Close', 'MA5', 'MA20', 'Next Diff %', 'RSI']] = False
    tickers.set_index('Symbol', drop=False, inplace=True)
    # tickers_top500 = tickers.nlargest(500, 'Market Cap')
    collection_period = '5d'
    collection_interval = '90m'
    raw_data: pd.DataFrame = yf.download(tickers=tickers['Symbol'].to_list(),
                                         period=collection_period,
                                         interval=collection_interval,
                                         group_by='ticker',
                                         threads=True)
    raw_data.reset_index(drop=False, inplace=True, names='DateTime')

    for smbl in tqdm(tickers.index, total=len(tickers)):
        tickers.loc[smbl, ['Close to crossover', 'Close', 'MA5', 'MA20', 'Next Diff %', 'RSI']] = \
            compute(smbl, raw_data, 20, 5)

    tickers = tickers[tickers['Close to crossover']].sort_values(by='RSI', ascending=False)
    tickers.to_excel('Data.xlsx')


if __name__ == '__main__':
    main()
