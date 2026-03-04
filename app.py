import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

st.title("Simple Crypto Dashboard")

st.write("Live Bitcoin price data from CoinGecko")

# Fetch data
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {
    "vs_currency": "usd",
    "days": "365"
}

r = requests.get(url, params=params)
data = r.json()

prices = data["prices"]

df = pd.DataFrame(prices, columns=["timestamp", "price"])
df["date"] = pd.to_datetime(df["timestamp"], unit="ms")

# Sidebar controls
days = st.sidebar.slider("Days to display", 7, 365, 90)

filtered = df.tail(days)

# Metrics
latest_price = filtered["price"].iloc[-1]
st.metric("Latest BTC Price", f"${latest_price:,.2f}")

# Chart
fig = px.line(filtered, x="date", y="price", title="Bitcoin Price")

st.plotly_chart(fig, use_container_width=True)

# Show raw data
with st.expander("Show raw data"):
    st.dataframe(filtered)