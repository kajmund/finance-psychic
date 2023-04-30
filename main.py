import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import talib
import yfinance as yf

default_tickers = ['GOOG', 'AAPL', 'ERIC']
stocks = ['GOOG', 'AAPL', 'TSLA', 'MSFT', 'AMZN', 'ERIC']

st.write("### Välj aktier")
multiselection = st.multiselect(options=stocks, label='Aktier',
                                default=default_tickers
                                )
start = pd.to_datetime('2019/10/06')
end = pd.to_datetime('2023/04/29')

df = yf.download(multiselection, start, end)
st.write("##### Volym")
st.line_chart(df['Volume'], width=0, height=0, use_container_width=True)


def visualize_with_candlestick_foreach_stock(df, multiselection):
    for stock in multiselection:
        upper, middle, lower = talib.BBANDS(df["Close", stock], timeperiod=20)

        rsi = talib.RSI(df["Close", stock], timeperiod=14)
        df["upper", stock] = upper
        df["middle", stock] = middle
        df["lower", stock] = lower
        df["rsi", stock] = rsi
        df["sell", stock] = np.where(df["rsi", stock] < 30, df["Close", stock], np.nan)
        df["buy", stock] = np.where(df["rsi", stock] > 70, df["Close", stock], np.nan)
        print(df.head())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["upper", stock], name="BB High"))
        fig.add_trace(go.Scatter(x=df.index, y=df["middle", stock], name="BB Middle"))
        fig.add_trace(go.Scatter(x=df.index, y=df["lower", stock], name="BB Low"))

        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open', stock],
                                     high=df['High', stock],
                                     low=df['Low', stock],
                                     close=df['Close', stock],
                                     name=stock))
        fig.update_layout(title_text=f"{stock} Stock")
        fig.update_xaxes(rangeslider_visible=False)
        fig.add_trace(go.Scatter(x=df.index, y=df["buy", stock], name="RSI Köpläge", mode='markers',
                                 marker=dict(
                                     size=5,
                                     color='blue',
                                     symbol='circle',
                                     line=dict(width=2, color='black')
                                 )))

        fig.add_trace(go.Scatter(x=df.index, y=df["sell", stock], name="RSI Säljläge", mode='markers',
                                 marker=dict(
                                     size=5,
                                     color='red',
                                     symbol='circle',
                                     line=dict(width=2, color='black')
                                 )))
        fig.add_trace(go.Scatter(x=df.index, y=df["rsi", stock], name="RSI Kurva"))
        st.plotly_chart(fig)


visualize_with_candlestick_foreach_stock(df, multiselection)

if 'key' not in st.session_state:
    st.session_state['key'] = df

st.session_state.key = df
st.write(st.session_state.key)
