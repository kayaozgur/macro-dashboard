import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas_datareader import data as pdr

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

start = "2000-01-01"


def save_series(df: pd.DataFrame, filename: str, value_name: str):
    out = df.copy().reset_index()
    out.columns = ["date", value_name]
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    out.to_csv(data_dir / filename, index=False)


def save_placeholder(filename: str):
    df = pd.DataFrame(
        {"value": [None]},
        index=[pd.Timestamp(datetime.utcnow().date())]
    )
    save_series(df, filename, "value")


def fetch_fred_series(series_code: str, retries: int = 3, wait_seconds: int = 5):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            df = pdr.DataReader(series_code, "fred", start).dropna()
            return df
        except Exception as e:
            last_error = e
            print(f"{series_code} çekilemedi. Deneme {attempt}/{retries}. Hata: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)
    raise last_error


fred_series = {
    "us10y.csv": ("DGS10", "value"),
    "dxy.csv": ("DTWEXBGS", "value"),
    "oil.csv": ("DCOILBRENTEU", "value"),
}

for filename, (series_code, value_name) in fred_series.items():
    try:
        df = fetch_fred_series(series_code)
        save_series(df, filename, value_name)
        print(f"{filename} yazıldı.")
    except Exception as e:
        print(f"{filename} alınamadı, placeholder yazılıyor. Hata: {e}")
        save_placeholder(filename)

# Şimdilik placeholder bırakılan seriler
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
    save_placeholder(fname)
    print(f"{fname} placeholder olarak yazıldı.")

print("Data update completed.")