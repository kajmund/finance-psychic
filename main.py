import pandas as pd
import streamlit as st
import yfinance as yf

default_tickers = ['GOOG', 'AAPL','ERIC']
stocks = ['GOOG', 'AAPL', 'TSLA', 'MSFT', 'AMZN','ERIC']

st.write("### Välj aktier")
multiselection = st.multiselect(options=stocks, label='Aktier',
                                default=default_tickers
                                )
start = pd.to_datetime('2021/10/06')
end = pd.to_datetime('2022/10/06')

df = yf.download(multiselection, start, end)['Close']
print(df.head())

if 'key' not in st.session_state:
    st.session_state['key'] = df

st.session_state.key = df
st.write(st.session_state.key)
