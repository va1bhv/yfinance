import asyncio
from asyncio import Task

import pandas as pd
import yfinance as yf


def get_data(tkr, collection_period='8d', collection_interval='90m', rolling_up=20, rolling_down=5):
    try:
        dt = yf.download(tickers=tkr, period=collection_period, interval=collection_interval)
        # Adding Moving average calculated field
        # dt['MA5'] = dt['Close'].rolling(rolling_down).mean()
        # dt['MA20'] = dt['Close'].rolling(rolling_up).mean()
        # dt['Diff'] = (dt['MA20'] - dt['MA5']) / dt['MA20']
        return dt
    except KeyError:
        return -1


async def get_data_async(tkr: str) -> pd.DataFrame:
    kw = dict(
        collection_period='8d',
        collection_interval='90m',
        rolling_up=20,
        rolling_down=5
    )
    data: pd.DataFrame = await asyncio.to_thread(yf.download, tkr, None)

    return data


async def main() -> None:
    sbi_task: Task[pd.DataFrame] = asyncio.create_task(get_data_async('SBIN.NS'))
    infy_task: Task[pd.DataFrame] = asyncio.create_task(get_data_async('INFY.NS'))
    itc_task: Task[pd.DataFrame] = asyncio.create_task(get_data_async('ITC.NS'))
    titan_task: Task[pd.DataFrame] = asyncio.create_task(get_data_async('TITAN.NS'))

    ans = {'sbi': None, }
    ans['sbi'] = await sbi_task
    ans['infy'] = await infy_task
    ans['itc'] = await itc_task
    ans['titan'] = await titan_task

    print(ans)


if __name__ == '__main__':
    asyncio.run(main=main())
