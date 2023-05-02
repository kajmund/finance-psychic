import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from backtesting.supertrend import backtest_supertrend

default_tickers = ['GOOG', 'AAPL', 'ERIC', 'NOK']
stocks = ['GOOG', 'AAPL', 'TSLA', 'MSFT', 'AMZN', 'ERIC', 'NOK', 'META', 'BABA', 'TSM', 'NVDA', 'ASML', 'ADBE', 'PYPL']

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
        bbands = ta.bbands(close=df["Close", stock], length=20)
        rsi = ta.rsi(df["Close", stock], length=20)
        stock_df = df[[('Open', stock), ('High', stock), ('Low', stock), ('Close', stock)]]
        stock_df.columns = ['Open', 'High', 'Low', 'Close']
        supertrend_data = supertrend(stock_df, atr_period=10, multiplier=3)

        df["upper", stock] = bbands["BBU_20_2.0"]
        df["middle", stock] = bbands["BBM_20_2.0"]
        df["lower", stock] = bbands["BBL_20_2.0"]
        df["rsi", stock] = rsi
        df["Supertrend", stock] = supertrend_data["Supertrend"]
        df["Final Lowerband", stock] = supertrend_data["Final Lowerband"]
        df["Final Upperband", stock] = supertrend_data["Final Upperband"]

        print(df["Supertrend", stock])


        df["sell", stock] = np.where(df["rsi", stock] < 30, df["Close", stock], np.nan)
        df["buy", stock] = np.where(df["rsi", stock] > 70, df["Close", stock], np.nan)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["upper", stock], name="BB High"))
        fig.add_trace(go.Scatter(x=df.index, y=df["middle", stock], name="BB Middle"))
        fig.add_trace(go.Scatter(x=df.index, y=df["lower", stock], name="BB Low"))
        fig.add_trace(go.Scatter(x=df.index, y=df["Supertrend", stock], name="SuperTrend"))
        fig.add_trace(go.Scatter(x=df.index, y=df["Final Lowerband", stock], name="ST LB"))
        fig.add_trace(go.Scatter(x=df.index, y=df["Final Upperband", stock], name="ST UB"))
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

        entry, exit, roi = backtest_supertrend(df, stock, 100000)
        st.write(f"Supertrend ROI: {roi} %")
        #st.write(f"Entry: {entry}")
        #st.write(f"Exit: {exit}")



def supertrend(df, atr_period, multiplier):
    high = df['High']
    low = df['Low']
    close = df['Close']

    # calculate ATR
    price_diffs = [high - low,
                   high - close.shift(),
                   close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1 / atr_period, min_periods=atr_period).mean()
    # df['atr'] = df['tr'].rolling(atr_period).mean()

    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)

    # initialize Supertrend column to True
    supertrend = [True] * len(df)

    for i in range(1, len(df.index)):
        curr, prev = i, i - 1

        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

            # adjustment to the final bands
            if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                final_lowerband[curr] = final_lowerband[prev]
            if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr]:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan

    return pd.DataFrame({
        'Supertrend': supertrend,
        'Final Lowerband': final_lowerband,
        'Final Upperband': final_upperband
    }, index=df.index)



visualize_with_candlestick_foreach_stock(df, multiselection)

if 'key' not in st.session_state:
    st.session_state['key'] = df

st.session_state.key = df
st.write(st.session_state.key)
