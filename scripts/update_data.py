from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def save_price_series(df: pd.DataFrame, filename: str) -> None:
    if df is None or df.empty:
        save_placeholder(filename)
        return

    out = df.copy().reset_index()

    # Yahoo genelde Date + Close döndürür
    if "Date" not in out.columns:
        out.rename(columns={out.columns[0]: "Date"}, inplace=True)

    if "Close" not in out.columns:
        save_placeholder(filename)
        return

    out = out[["Date", "Close"]]
    out.columns = ["date", "value"]
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["date", "value"])

    if out.empty:
        save_placeholder(filename)
        return

    out.to_csv(DATA_DIR / filename, index=False)


def save_placeholder(filename: str) -> None:
    pd.DataFrame(
        {"date": [datetime.utcnow().strftime("%Y-%m-%d")], "value": [None]}
    ).to_csv(DATA_DIR / filename, index=False)


def fetch_yahoo_series(ticker: str, period: str = "max") -> pd.DataFrame:
    df = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    return df
    
def fetch_fred_series(series_code):
    try:
        df = pdr.DataReader(series_code, "fred")
        df = df.reset_index()
        df.columns = ["date", "value"]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df
    except Exception as e:
        print(f"{series_code} alınamadı: {e}")
        return None


# Gerçek veri çekilecek seriler
yahoo_map = {
    "us10y.csv": "^TNX",
    "dxy.csv": "DX-Y.NYB",
    "oil.csv": "BZ=F",
    "usdtry.csv": "TRY=X"
}

for filename, ticker in yahoo_map.items():
    try:
        df = fetch_yahoo_series(ticker)
        save_price_series(df, filename)
        print(f"{filename} başarıyla yazıldı.")
    except Exception as e:
        print(f"{filename} alınamadı, placeholder yazılıyor. Hata: {e}")
        save_placeholder(filename)

# TCMB rezervleri
try:
    reserves = fetch_fred_series("TRESEGTRM052N")
    if reserves is not None and not reserves.empty:
        reserves.to_csv(DATA_DIR / "reserves.csv", index=False)
        print("reserves.csv başarıyla yazıldı.")
    else:
        save_placeholder("reserves.csv")
        print("reserves.csv placeholder olarak yazıldı.")
except Exception as e:
    save_placeholder("reserves.csv")
    print(f"reserves.csv alınamadı: {e}")

# Şimdilik placeholder kalan seriler
placeholder_files = [
    "m2.csv",
    "policy_rate.csv",
    "tr10y.csv",
    "cds.csv",
    "bist_usd.csv",
]

for filename in placeholder_files:
    save_placeholder(filename)
    print(f"{filename} placeholder olarak yazıldı.")

print("Data update completed.")