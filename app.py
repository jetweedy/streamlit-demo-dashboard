import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Dashboard Template", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/vega/vega-datasets/master/data/seattle-weather.csv"

@st.cache_data(ttl=3600)
def load_data(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.StringIO(r.text))
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data(DATA_URL)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

weather_options = ["(All)"] + sorted(df["weather"].dropna().unique().tolist())
weather_choice = st.sidebar.selectbox("Weather type", weather_options, index=0)

temp_metric = st.sidebar.selectbox("Temperature metric", ["temp_max", "temp_min", "wind", "precipitation"], index=0)

search = st.sidebar.text_input("Search (free text)", value="")

# Normalize date_range output (Streamlit returns a date or tuple depending on UI)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
filtered = df.loc[mask].copy()

if weather_choice != "(All)":
    filtered = filtered[filtered["weather"] == weather_choice]

if search.strip():
    s = search.strip().lower()
    # Search across a few sensible columns
    filtered = filtered[
        filtered["weather"].astype(str).str.lower().str.contains(s)
        | filtered["date"].astype(str).str.lower().str.contains(s)
    ]

# -----------------------------
# Header + KPIs
# -----------------------------
st.title("Streamlit Dashboard Template")
st.caption("Example dataset: Seattle daily weather (Vega datasets).")

c1, c2, c3, c4 = st.columns(4)

rows = len(filtered)
avg_val = float(filtered[temp_metric].mean()) if rows else 0.0
max_val = float(filtered[temp_metric].max()) if rows else 0.0
min_val = float(filtered[temp_metric].min()) if rows else 0.0

c1.metric("Rows", f"{rows:,}")
c2.metric(f"Average {temp_metric}", f"{avg_val:,.2f}")
c3.metric(f"Max {temp_metric}", f"{max_val:,.2f}")
c4.metric(f"Min {temp_metric}", f"{min_val:,.2f}")

st.divider()

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader(f"Trend: {temp_metric} over time")
    if rows:
        fig_line = px.line(filtered.sort_values("date"), x="date", y=temp_metric)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data matches your filters.")

with right:
    st.subheader("Weather type breakdown")
    if rows:
        counts = filtered["weather"].value_counts().reset_index()
        counts.columns = ["weather", "count"]
        fig_bar = px.bar(counts, x="weather", y="count")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data to chart.")

st.divider()

# -----------------------------
# Data table
# -----------------------------
st.subheader("Data")
st.write("Sort, scroll, and copy from here. Use the sidebar search to filter.")
st.dataframe(
    filtered.sort_values("date", ascending=False),
    use_container_width=True,
    hide_index=True,
)

with st.expander("Show notes / how to extend"):
    st.markdown(
        """
**Easy upgrades**
- Add more filters (sliders for wind/precip).
- Add a rolling average: `filtered[temp_metric].rolling(7).mean()`.
- Add downloads: `st.download_button(...)`.
- Swap dataset + charts, keep the layout.
        """
    )