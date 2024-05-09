import warnings

import pandas as pd
import streamlit as st

from canclestick_graph import draw
from dataProcess import compute
from download_data import download_data
from readData import read_data

warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="Stonks",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    st.title('📈💰📊 Stonks')
    with st.form(key='number-of-tickers'):
        st.write('Choose number of tickers to compare')
        num_tickers = st.slider(
            label='Filtered by market cap',
            min_value=50,
            max_value=2255,
            value=500
        )
        num_tickers_btn = st.form_submit_button(
            label="Submit",
            help=None,
            use_container_width=True)

        tickers = read_data(num_tickers)
        if num_tickers_btn:
            tickers = read_data(num_tickers)
            st.write(tickers['Company Name'])
            st.caption('Ticker list loaded!')

    with st.form(key='hyper-parameters'):

        st.write('Choose hyper parameters')
        collection_period = st.select_slider(
            label='Collection period (Range)',
            options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
            value='1mo'
        )
        collection_interval = st.select_slider(
            label='Collection interval (Granularity)',
            options=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
            value='90m'
        )
        rolling_up = st.slider(
            label='Long term moving average duration',
            min_value=10,
            max_value=50,
            value=20
        )
        rolling_down = st.slider(
            label='Short term moving average duration',
            min_value=1,
            max_value=10,
            value=5
        )
        negative_diff_width = st.slider(
            label='Number of rows to apply non-positive condition for',
            min_value=1,
            max_value=10,
            value=5
        )
        negative_diff_tolerance = st.slider(
            label='Maximum number of positives allowed',
            min_value=1,
            max_value=5,
            value=2,
        )
        hyper_params_btn = st.form_submit_button(
            label="Submit",
            help=None,
            use_container_width=True,
        )
        st.session_state.hyper_params_btn = hyper_params_btn
        if hyper_params_btn:
            st.write('Collecting raw data (It might a few minutes, please be patient)')
            raw_data: pd.DataFrame = download_data(
                tickers=tickers['Symbol'].to_list(),
                collection_period=collection_period,
                collection_interval=collection_interval
            )

            for smbl in tickers.index:
                tickers.loc[smbl, ['Close to crossover', 'Close', 'MA5', 'MA20', 'Next Diff %', 'RSI']] = \
                    compute(smbl, rolling_up=rolling_up, rolling_down=rolling_down,
                            width=negative_diff_width, tolerance=negative_diff_tolerance, raw_data=raw_data)
            tickers = tickers[tickers['Close to crossover']].sort_values(by='RSI', ascending=False)
            st.write('Data downloaded')
            # st.dataframe(tickers)
            st.session_state.raw_data = raw_data
            st.session_state.tickers = tickers
            st.session_state.rolling_up = rolling_up
            st.session_state.rolling_down = rolling_down
with st.container(border=True):
    try:
        tickers = st.session_state.tickers
        raw_data = st.session_state.raw_data
        rolling_up = st.session_state.rolling_up
        rolling_down = st.session_state.rolling_down
        hyper_params_btn = st.session_state.hyper_params_btn
    except AttributeError:
        tickers = pd.DataFrame(
            columns=['Symbol', 'Company Name', 'Market Cap', 'Close to crossover', 'Close',
                     'MA5', 'MA20', 'Next Diff %', 'RSI']
        )
    chosen_tickers = st.multiselect(
        "Choose tickers to view",
        tickers['Symbol'].values,
    )
    hyper_params_btn = st.session_state.hyper_params_btn

    with st.container():
        tabs = st.tabs(['All', *chosen_tickers])
        all_tab = tabs[0]
        with all_tab:
            # if not hyper_params_btn:
            #     tickers = pd.DataFrame(
            #         columns=['Symbol', 'Company Name', 'Market Cap', 'Close to crossover', 'Close',
            #                  'MA5', 'MA20', 'Next Diff %', 'RSI']
            #     )
            st.dataframe(
                data=tickers.drop(columns=['MA5', 'MA20', 'Close to crossover']),
                use_container_width=True
            )
        for tab, tkr in zip(tabs[1:], chosen_tickers):
            with tab:
                fig, data = draw(raw_data[tkr], rolling_up, rolling_down)
                st.plotly_chart(
                    figure_or_data=fig,
                    use_container_width=True,
                )
                with st.expander(label='Raw data'):
                    st.dataframe(data, use_container_width=True)
