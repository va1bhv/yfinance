import numpy as np
import pandas as pd
import yfinance as yf
from tqdm import tqdm
import logging
logger = logging.getLogger('yfinance')
logger.disabled = True
logger.propagate = False

tqdm.pandas()


def get_data(tkr, collection_period='5d', collection_interval='90m', rolling_up=20, rolling_down=5):
    try:
        dt = yf.download(tickers=tkr, period=collection_period, interval=collection_interval)
        # Adding Moving average calculated field
        dt['MA5'] = dt['Close'].rolling(rolling_down).mean()
        dt['MA20'] = dt['Close'].rolling(rolling_up).mean()
        dt['%Diff'] = ((dt['MA20'] - dt['MA5'])/dt['MA20']) * 100
        dt.dropna(inplace=True)
        return dt
    except KeyError:
        return None


def rsi(dta, window=14, adjust=False):
    delta = dta['Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    rs = gain_ewm / loss_ewm
    rsi = 100 - 100 / (1 + rs)

    return rsi


tickers = pd.read_excel("MCAP28032024.xlsx")
tickers = tickers.drop(columns=['Sr. No.', 'Market capitalization as on March 28, 2024\n(In lakhs)'])
tickers['Symbol'] = tickers['Symbol'] + '.NS'
tickers['Close to crossover'] = 0
# tickers['Data'] = tickers['Symbol'].head(50).progress_apply(get_data)

for i in tqdm(range(len(tickers))):
    temp = get_data(tickers.iloc[i, 0])
    try:
        if np.argmin(np.abs(temp['Diff'].fillna(np.inf).values)) < len(temp) - 3:
            tickers.loc[i, 'Close to crossover'] = False
        else:
            tickers.loc[i, 'Close to crossover'] = True
    except ValueError:
        tickers.loc[i, 'Close to crossover'] = -1

# data = get_data(tickers.iloc[0, 0])
# fig = go.Figure()

# # Candlestick
# fig.add_trace(go.Candlestick(x=data.index,
#                              open=data['Open'],
#                              high=data['High'],
#                              low=data['Low'],
#                              close=data['Close'], name='market data'))
#
# # Add Moving average on the graph
# fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], line=dict(color='blue', width=1.5), name='Long Term MA'))
# fig.add_trace(go.Scatter(x=data.index, y=data['MA5'], line=dict(color='orange', width=1.5), name='Short Term MA'))
#
# # Updating X axis and graph
# # X-Axes
# fig.update_xaxes(
#     rangeslider_visible=True,
#     rangeselector=dict(
#         buttons=list([
#             dict(count=3, label="3d", step="day", stepmode="backward"),
#             dict(count=5, label="5d", step="day", stepmode="backward"),
#             dict(count=7, label="WTD", step="day", stepmode="todate"),
#             dict(step="all")
#         ])
#     )
# )
#
# # Show
# # fig.write_html(f'data/{ticker}_data.html', auto_open=True)
# fig.show()

tk = tickers.iloc[6, 0]
df = get_data(tk)

a = get_data('TATAPOWER.NS')

for i in tqdm(range(len(tickers))):
    temp = get_data(tickers.iloc[i, 0])
    if temp is None:
        tickers.loc[i, 'Close to crossover'] =
        continue
    else:
        if np.argmin(np.abs(temp['Diff'].fillna(np.inf).values)) < (len(temp) - 3):
            tickers.loc[i, 'Close to crossover'] = False
        else:
            tickers.loc[i, 'Close to crossover'] = True
