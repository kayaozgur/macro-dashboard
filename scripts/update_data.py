import time
from io import StringIO
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "macro-dashboard/1.0"
}


def save_series(df: pd.DataFrame, filename: str) -> None:
    df = df.copy()
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(DATA_DIR / filename, index=False)


def save_placeholder(filename: str) -> None:
    pd.DataFrame(
        {"date": [datetime.utcnow().strftime("%Y-%m-%d")], "value": [None]}
    ).to_csv(DATA_DIR / filename, index=False)


def fetch_fred_csv(series_code: str, retries: int = 3, wait_seconds: int = 5) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_code}"
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            resp.raise_for_status()

            df = pd.read_csv(StringIO(resp.text))
            if df.shape[1] < 2:
                raise ValueError(f"{series_code} beklenen CSV formatında değil.")

            df = df.iloc[:, :2]
            if df.empty:
                raise ValueError(f"{series_code} boş döndü.")

            return df

        except Exception as e:
            last_error = e
            print(f"{series_code} alınamadı. Deneme {attempt}/{retries}. Hata: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)

    raise last_error if last_error else Exception(f"{series_code} verisi alınamadı.")


# FRED'den gerçek veri çekilecek seriler
fred_files = {
    "us10y.csv": "DGS10",
    "dxy.csv": "DTWEXBGS",
    "oil.csv": "DCOILBRENTEU",
}

for filename, series_code in fred_files.items():
    try:
        df = fetch_fred_csv(series_code)
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