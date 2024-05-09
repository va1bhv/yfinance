import pandas as pd
import plotly.graph_objs as go


def draw(data: pd.DataFrame, rolling_up: int, rolling_down: int) -> tuple[go.Figure, pd.DataFrame]:
    data['MA5'] = data['Close'].rolling(rolling_down).mean()
    data['MA20'] = data['Close'].rolling(rolling_up).mean()
    data['%Diff'] = ((data['MA5'] - data['MA20']) / data['MA5']) * 100
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Market Data',
            visible='legendonly'
        ),
    )

    # Add Moving average on the graph
    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], line=dict(width=2), name='Long Term MA'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA5'], line=dict(width=2), name='Short Term MA'))
    # fig.add_trace(go.Scatter(x=data.index, y=data['Close'], line=dict(color='red', width=1.5), name='Close'))
    # fig.add_trace(go.Scatter(x=data.index, y= data['%Diff'],line=dict(color='orange', width=1.5), name = '%Diff'))

    # Updating X axis and graph
    # X-Axes
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=3, label="3d", step="day", stepmode="backward"),
                dict(count=5, label="5d", step="day", stepmode="backward"),
                dict(count=7, label="WTD", step="day", stepmode="todate"),
                dict(step="all")
            ])
        )
    )

    # Show
    # fig.write_html(f'data/{ticker}_data.html', auto_open=True)
    # fig.update_xaxes(gridcolor='white')
    # fig.update_yaxes(gridcolor='white')
    fig.update_layout(template='plotly_dark')
    return fig, data
