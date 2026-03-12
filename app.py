import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
META_FILE = BASE / "metadata" / "descriptions.json"

st.set_page_config(page_title="Makro Dashboard", layout="wide")

with open(META_FILE, "r", encoding="utf-8") as f:
    DESCRIPTIONS = json.load(f)

SERIES_FILES = {
    "CDS": "cds.csv",
    "M2": "m2.csv",
    "USDTRY": "usdtry.csv",
    "RESERVES": "reserves.csv",
    "POLICY_RATE": "policy_rate.csv",
    "US10Y": "us10y.csv",
    "DXY": "dxy.csv",
    "OIL": "oil.csv",
    "TR10Y": "tr10y.csv",
    "BIST_USD": "bist_usd.csv",
    "BIST": "bist.csv",
}

RISK = ["CDS", "USDTRY", "RESERVES"]
LIQ = ["M2", "POLICY_RATE"]
GLOBAL = ["US10Y", "DXY", "OIL"]
LOCAL = ["TR10Y", "BIST_USD"]

def read_series(key):
    path = DATA_DIR / SERIES_FILES[key]
    df = pd.read_csv(path)

    if "date" not in df.columns:
        return pd.DataFrame({"date": [], "value": []})

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df = df.dropna(subset=["value"])

    return df

def plot_small(df, title):
    val_col = [c for c in df.columns if c != "date"][0]
    fig = px.line(df, x="date", y=val_col, title=title)
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

def render_group(title, keys):
    st.subheader(title)
    cols = st.columns(len(keys))
    for col, key in zip(cols, keys):
        with col:
            df = read_series(key)
            val_col = [c for c in df.columns if c != "date"][0]
            last = df[val_col].dropna()
            last_text = "N/A" if last.empty else f"{last.iloc[-1]:,.2f}"
            st.metric(DESCRIPTIONS[key]["title"], last_text)
            plot_small(df, DESCRIPTIONS[key]["title"])

st.title("Makro Dashboard")

render_group("Risk", RISK)
render_group("Likidite", LIQ)
render_group("Küresel", GLOBAL)
render_group("Yerel Piyasa", LOCAL)

st.divider()

selected = st.selectbox(
    "Detay gösterge",
    list(SERIES_FILES.keys()),
    format_func=lambda x: DESCRIPTIONS[x]["title"]
)

df = read_series(selected)
val_col = [c for c in df.columns if c != "date"][0]

fig = px.line(df, x="date", y=val_col, title=DESCRIPTIONS[selected]["title"])
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"**Ne anlama gelir:** {DESCRIPTIONS[selected]['meaning']}")
st.markdown(f"**Dikkat edilmesi gerekenler:** {DESCRIPTIONS[selected]['watch']}")
