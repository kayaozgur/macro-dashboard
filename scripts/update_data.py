import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas_datareader import data as pdr

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)


def save_series(df: pd.DataFrame, filename: str):
    out = df.copy().reset_index()

    # İlk sütun tarih olsun
    first_col = out.columns[0]
    value_col = out.columns[1]

    out = out[[first_col, value_col]]
    out.columns = ["date", "value"]

    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")

    out.to_csv(data_dir / filename, index=False)


def save_placeholder(filename: str):
    df = pd.DataFrame(
        {
            "date": [datetime.utcnow().strftime("%Y-%m-%d")],
            "value": [None],
        }
    )
    df.to_csv(data_dir / filename, index=False)


def fetch_fred_series(series_code: str, start="2000-01-01", retries=3, wait_seconds=5):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            df = pdr.DataReader(series_code, "fred", start).dropna()
            if not df.empty:
                return df
        except Exception as e:
            last_error = e
            print(f"{series_code} alınamadı. Deneme {attempt}/{retries}. Hata: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)

    raise last_error if last_error else Exception(f"{series_code} verisi alınamadı.")


# FRED'den gerçek veri çekilen seriler
fred_files = {
    "us10y.csv": "DGS10",
    "dxy.csv": "DTWEXBGS",
    "oil.csv": "DCOILBRENTEU",
}

for filename, series_code in fred_files.items():
    try:
        df = fetch_fred_series(series_code)
        save_series(df, filename)
        print(f"{filename} başarıyla yazıldı.")
    except Exception as e:
        print(f"{filename} için veri alınamadı, placeholder yazılıyor. Hata: {e}")
        save_placeholder(filename)


# Şimdilik placeholder kalan seriler
placeholder_files = [
    "usdtry.csv",
    "m2.csv",
    "policy_rate.csv",
    "reserves.csv",
    "tr10y.csv",
    "cds.csv",
    "bist_usd.csv",
]

for filename in placeholder_files:
    save_placeholder(filename)
    print(f"{filename} placeholder olarak yazıldı.")

print("Data update completed.")