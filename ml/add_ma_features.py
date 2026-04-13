# Moving averages
def add_features(df):
    df = df.copy()
    df['ma_7'] = df['close'].rolling(7).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['ma_50'] = df['close'].rolling(50).mean()

    # Convert to %
    df['ma7_pct']  = (df['close'] - df['ma_7']) / df['ma_7'] * 100
    df['ma20_pct'] = (df['close'] - df['ma_20']) / df['ma_20'] * 100
    df['ma50_pct'] = (df['close'] - df['ma_50']) / df['ma_50'] * 100

    feature_cols = [
        'ma7_pct', 'ma20_pct', 'ma50_pct']
    df[feature_cols] = df[feature_cols].shift(1)
    df = df.dropna().reset_index(drop=True)
    return df, feature_cols
