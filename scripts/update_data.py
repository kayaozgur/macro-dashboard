import pandas as pd
from pandas_datareader import data as pdr
from pathlib import Path
from datetime import datetime

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

start = "2000-01-01"

def save_series(df: pd.DataFrame, filename: str, value_name: str):
    out = df.copy().reset_index()
    out.columns = ["date", value_name]
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(data_dir / filename, index=False)

# US10Y
us10y = pdr.DataReader("DGS10", "fred", start).dropna()
save_series(us10y, "us10y.csv", "value")

# DXY
dxy = pdr.DataReader("DTWEXBGS", "fred", start).dropna()
save_series(dxy, "dxy.csv", "value")

# Brent Oil
oil = pdr.DataReader("DCOILBRENTEU", "fred", start).dropna()
save_series(oil, "oil.csv", "value")

# Placeholder seriler
placeholder_files = [
    "usdtry.csv",
    "m2.csv",
    "policy_rate.csv",
    "reserves.csv",
    "tr10y.csv",
    "cds.csv",
    "bist_usd.csv"
]

for fname in placeholder_files:
    df = pd.DataFrame(
        {"value": [None]},
        index=[pd.Timestamp(datetime.utcnow().date())]
    )
    save_series(df, fname, "value")

print("Data update completed.")
