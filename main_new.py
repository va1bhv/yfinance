import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm

tqdm.pandas()


def get_data(tkr, collection_period='10d', collection_interval='90m', rolling_up=20, rolling_down=5):
    dt = yf.download(tickers=tkr, period=collection_period, interval=collection_interval)
    if dt is not None:
        # Adding Moving average calculated field
        dt['MA5'] = dt['Close'].rolling(rolling_down).mean()
        dt['MA20'] = dt['Close'].rolling(rolling_up).mean()
        dt['%Diff'] = ((dt['MA20'] - dt['MA5']) / dt['MA20']) * 100
        # dt['Gradient'] = np.gradient(dt['%Diff'])
        dt.dropna(inplace=True)
    else:
        dt = None
    return dt


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


# a = get_data('TATAPOWER.NS')


# Function to determine the order of ARIMA model
# def find_arima_order(time_series):
#     # Step 2: Check stationarity
#     result = adfuller(time_series)
#     stationary = False
#     if result[1] < 0.05:  # p-value threshold
#         stationary = True
#         d = 0
#     else:
#         d = 1
#
#     # Step 3: Plot ACF and PACF
#     if stationary:
#         plot_acf(time_series)
#         plot_pacf(time_series)
#         plt.show()
#
#     # Step 4: Grid search for p and q
#     best_aic = np.inf
#     best_order = None
#     for p in range(3):
#         for q in range(3):
#             try:
#                 model = ARIMA(time_series, order=(p, d, q))
#                 fitted_model = model.fit()
#                 aic = fitted_model.aic
#                 if aic < best_aic:
#                     best_aic = aic
#                     best_order = (p, d, q)
#             except:
#                 pass
#
#     return best_order


# Example usage:
# a = get_data('SBIN.NS')
# a.reset_index(drop=True, inplace=True)
# ts = a.loc[:, '%Diff'].values
# order = find_arima_order(ts)
# print("Best ARIMA order:", order)

# Order to be used will be (1, 1, 0)

def predict_next_number_arima(time_series):
    """
    Predict the next number in a time series using the ARIMA model.

    Parameters:
        time_series (list): A list of numbers representing the time series.

    Returns:
        float: The predicted next number in the time series.
    """
    # Convert the time series to numpy array
    time_series = np.array(time_series)

    # Fit ARIMA model
    model = ARIMA(time_series, order=(1, 1, 0))  # Example order, you may need to adjust
    fitted_model = model.fit()

    # Forecast the next value
    forecast = fitted_model.forecast(steps=1)

    # Extract the forecasted value
    next_number = forecast[0]

    return next_number


# Example usage:
a = get_data('TATAPOWER.NS')
a.reset_index(drop=True, inplace=True)
ts = a.loc[range(4, 19), '%Diff'].values
nn = predict_next_number_arima(ts)
print("Next number prediction (ARIMA):", nn)
