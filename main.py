import warnings

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

tickers = pd.read_excel("MCAP28032024.xlsx")

tickers = tickers.drop(columns=['Sr. No.'])
tickers.rename(columns={'Market capitalization as on March 28, 2024\n(In lakhs)': 'Market Cap'}, inplace=True)
tickers['Symbol'] = tickers['Symbol'] + '.NS'
tickers[['Close to crossover', 'Next Diff', 'RSI']] = False
tickers.set_index('Symbol', drop=False, inplace=True)
tickers_top500 = tickers.nlargest(500, 'Market Cap')
collection_period = '5d'
collection_interval = '90m'
raw_data: pd.DataFrame = yf.download(tickers=tickers_top500['Symbol'].to_list(),
                                     period=collection_period,
                                     interval=collection_interval,
                                     group_by='ticker',
                                     threads=True)
raw_data.reset_index(drop=False, inplace=True, names='DateTime')


def get_data(tkr, rolling_up=20, rolling_down=5) -> pd.DataFrame:
    dt = raw_data[tkr]
    dt['MA5'] = dt['Close'].rolling(rolling_down).mean()
    dt['MA20'] = dt['Close'].rolling(rolling_up).mean()
    dt['%Diff'] = ((dt['MA5'] - dt['MA20']) / dt['MA5']) * 100
    dt.dropna(inplace=True)
    return dt


def rsi(dta, window=14, adjust=False) -> float:
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


def compute(tkr: str) -> tuple[bool, float, float]:
    """
    :param tkr: Symbol to fetch the raw_data for
    :return close_to_crossover: if the difference between the moving averages will cross over
            nn: forecasted difference next in the time series
            rsi: the computed rsi of the latest raw_data
    """
    temp = get_data(tkr)
    temp.reset_index(inplace=True, names='DateTime')
    time_series = temp['%Diff'].values

    if temp.empty or any(time_series[-3:] < 0):
        return False, -1, -1

    nn = ARIMA(time_series, order=(1, 1, 0)).fit().forecast(steps=1)[0]
    if nn < 0:
        return False, nn, -1

    return True, nn, rsi(temp)


for smbl in tqdm(tickers_top500.index, total=len(tickers_top500)):
    tickers_top500.loc[smbl, ['Close to crossover', 'Next Diff', 'RSI']] = compute(smbl)

tickers_top500 = tickers_top500[tickers_top500['Close to crossover']].sort_values(by='RSI', ascending=False)
