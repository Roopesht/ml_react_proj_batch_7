import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model.pickle"
DATA_PATH = BASE_DIR.parent / "ml" / "data.csv"

# =========================
# LOAD MODEL
# =========================
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# =========================
# FEATURE LIST (must match training)
# =========================
FEATURE_COLS = [
    'ma7_pct', 'ma20_pct', 'ma50_pct',
    'ma7_20_pct', 'ma20_50_pct',
    'ret_1', 'ret_3', 'ret_5',
    'range_pct', 'range_mean_5', 'range_std_5',
    'atr_pct',
    'gap_pct',
    'body_pct', 'upper_wick', 'lower_wick',
    'breakout_up', 'breakout_down',
    'vol_pct',
    'gap_x_range', 'trend_x_vol'
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def load_and_prepare() -> pd.DataFrame:
    """Load data.csv, filter NIFTY, compute indicators (no shift — for live prediction)."""
    df = pd.read_csv(DATA_PATH)
    df = df[df["SYMBOL"] == "NIFTY"]
    df = df[["ADATE", "OPEN", "HIGH", "LOW", "CLOSE", "TOTTRDQTY"]]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df = df.reset_index(drop=True)

    # --- Moving averages ---
    df['ma_7']  = df['close'].rolling(7).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['ma_50'] = df['close'].rolling(50).mean()

    # --- Trend ---
    df['ma7_pct']    = (df['close'] - df['ma_7'])  / df['ma_7']  * 100
    df['ma20_pct']   = (df['close'] - df['ma_20']) / df['ma_20'] * 100
    df['ma50_pct']   = (df['close'] - df['ma_50']) / df['ma_50'] * 100
    df['ma7_20_pct'] = (df['ma_7']  - df['ma_20']) / df['ma_20'] * 100
    df['ma20_50_pct']= (df['ma_20'] - df['ma_50']) / df['ma_50'] * 100

    # --- Momentum ---
    df['ret_1'] = df['close'].pct_change(1) * 100
    df['ret_3'] = df['close'].pct_change(3) * 100
    df['ret_5'] = df['close'].pct_change(5) * 100

    # --- Volatility ---
    df['range_pct']    = (df['high'] - df['low']) / df['close'] * 100
    df['range_mean_5'] = df['range_pct'].rolling(5).mean()
    df['range_std_5']  = df['range_pct'].rolling(5).std()

    # --- ATR ---
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low']  - df['close'].shift(1))
        )
    )
    df['atr_5']   = df['tr'].rolling(5).mean()
    df['atr_pct'] = df['atr_5'] / df['close'] * 100

    # --- Gap ---
    df['gap_pct'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1) * 100

    # --- Candle structure ---
    df['body_pct']   = (df['close'] - df['open']) / df['open'] * 100
    df['upper_wick'] = (df['high'] - np.maximum(df['open'], df['close'])) / df['open'] * 100
    df['lower_wick'] = (np.minimum(df['open'], df['close']) - df['low'])  / df['open'] * 100

    # --- Breakout ---
    df['rolling_high_5'] = df['high'].rolling(5).max()
    df['rolling_low_5']  = df['low'].rolling(5).min()
    df['breakout_up']    = (df['close'] > df['rolling_high_5'].shift(1)).astype(int)
    df['breakout_down']  = (df['close'] < df['rolling_low_5'].shift(1)).astype(int)

    # --- Volume ---
    df['vol_pct'] = df['volume'].pct_change() * 100

    # --- Interaction ---
    df['gap_x_range'] = df['gap_pct'] * df['range_pct']
    df['trend_x_vol'] = df['ma7_pct'] * df['range_pct']

    return df


@app.get("/pred_high")
def pred_high():
    df = load_and_prepare()

    # Last row with all features present
    last = df[FEATURE_COLS].dropna().iloc[-1]
    last_close = df.loc[df[FEATURE_COLS].dropna().index[-1], "close"]
    last_date  = df.loc[df[FEATURE_COLS].dropna().index[-1], "date"]

    X = last.values.reshape(1, -1)
    high_perc = float(model.predict(X)[0])

    predicted_high = round(last_close * (1 + high_perc / 100), 2)

    return {
        "based_on_date": last_date,
        "last_close": round(last_close, 2),
        "high_perc": round(high_perc, 4),
        "predicted_high": predicted_high,
    }
