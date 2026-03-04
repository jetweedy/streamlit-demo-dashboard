# Streamlit Dashboard Template

A simple Streamlit dashboard with:
- sidebar filters
- KPI metrics
- time-series chart + category chart
- searchable table
- cached data loading

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py