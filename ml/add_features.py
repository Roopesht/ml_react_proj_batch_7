import numpy as np

def add_features(df):
    df = df.copy()

    # =========================
    # MOVING AVERAGES
    # =========================
    df['ma_7'] = df['close'].rolling(7).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['ma_50'] = df['close'].rolling(50).mean()

    # =========================
    # TREND FEATURES
    # =========================
    df['ma7_pct']  = (df['close'] - df['ma_7']) / df['ma_7'] * 100
    df['ma20_pct'] = (df['close'] - df['ma_20']) / df['ma_20'] * 100
    df['ma50_pct'] = (df['close'] - df['ma_50']) / df['ma_50'] * 100

    df['ma7_20_pct']  = (df['ma_7'] - df['ma_20']) / df['ma_20'] * 100
    df['ma20_50_pct'] = (df['ma_20'] - df['ma_50']) / df['ma_50'] * 100

    # =========================
    # MOMENTUM
    # =========================
    df['ret_1'] = df['close'].pct_change(1) * 100
    df['ret_3'] = df['close'].pct_change(3) * 100
    df['ret_5'] = df['close'].pct_change(5) * 100

    # =========================
    # VOLATILITY
    # =========================
    df['range_pct'] = (df['high'] - df['low']) / df['close'] * 100
    df['range_mean_5'] = df['range_pct'].rolling(5).mean()
    df['range_std_5']  = df['range_pct'].rolling(5).std()

    # =========================
    # ATR
    # =========================
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )

    df['atr_5'] = df['tr'].rolling(5).mean()
    df['atr_pct'] = df['atr_5'] / df['close'] * 100

    # =========================
    # GAP
    # =========================
    df['gap_pct'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1) * 100

    # =========================
    # CANDLE STRUCTURE
    # =========================
    df['body_pct'] = (df['close'] - df['open']) / df['open'] * 100

    df['upper_wick'] = (df['high'] - np.maximum(df['open'], df['close'])) / df['open'] * 100
    df['lower_wick'] = (np.minimum(df['open'], df['close']) - df['low']) / df['open'] * 100

    # =========================
    # BREAKOUT FEATURES
    # =========================
    df['rolling_high_5'] = df['high'].rolling(5).max()
    df['rolling_low_5']  = df['low'].rolling(5).min()

    df['breakout_up'] = (df['close'] > df['rolling_high_5'].shift(1)).astype(int)
    df['breakout_down'] = (df['close'] < df['rolling_low_5'].shift(1)).astype(int)

    # =========================
    # VOLUME
    # =========================
    df['vol_pct'] = df['volume'].pct_change() * 100

    # =========================
    # INTERACTION FEATURES
    # =========================
    df['gap_x_range'] = df['gap_pct'] * df['range_pct']
    df['trend_x_vol'] = df['ma7_pct'] * df['range_pct']

    # =========================
    # FINAL FEATURE LIST
    # =========================
    feature_cols = [
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

    # =========================
    # SHIFT (CRITICAL - NO LEAKAGE)
    # =========================
    df[feature_cols] = df[feature_cols].shift(1)

    # =========================
    # CLEAN NA
    # =========================
    df = df.dropna().reset_index(drop=True)

    return df, feature_cols