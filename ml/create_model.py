import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data.csv")

# =========================
# CLEAN UP
# =========================
df = df[df["SYMBOL"] == 'NIFTY']

df = df[["ADATE","OPEN","HIGH","LOW","CLOSE","TOTTRDQTY"]]
df.columns = ["date","open","high","low","close","volume"]

df["high_perc"] = (df['high'] - df['close'].shift(1)) / df['close'].shift(1) * 100

#from add_ma_features import add_features
from add_features import add_features
df, features = add_features(df)

# =========================
# CLEAN NA
# =========================
df = df.dropna().reset_index(drop=True)

# =========================
# DATASET
# =========================
X = df[features]
y = df['high_perc']

# =========================
# SPLIT (TIME SERIES)
# =========================
split_index = int(len(df) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

#print(f"Total rows: {len(df)} | Train: {len(X_train)} | Test: {len(X_test)}")

# =========================
# MODEL
# =========================
model = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)
model.fit(X_train, y_train)

import pickle
file = open("model.pickle", "wb")
pickle.dump (model, file)

pred = model.predict(X_test)

# =========================
# METRICS
# =========================

# Error metrics
mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
r2 = r2_score(y_test, pred)

# Tolerance accuracy
tolerance = .4  # %
tol_accuracy = (np.abs(y_test - pred) <= tolerance).mean()
# Direction accuracy
direction_acc = (np.sign(y_test) == np.sign(pred)).mean()

# 1. Target Hit Accuracy (core metric)
hit_rate = (y_test >= pred).mean()

# 2. Conservative target (safer prediction)
adjusted_pred = pred * 0.8
adjusted_hit_rate = (y_test >= adjusted_pred).mean()

# 3. Overshoot (when market exceeded prediction)
overshoot = (y_test - pred)[y_test >= pred]
avg_overshoot = overshoot.mean() if len(overshoot) > 0 else 0

# 4. Miss (when prediction was too high)
miss = (pred - y_test)[y_test < pred]
avg_miss = miss.mean() if len(miss) > 0 else 0

# =========================
# OUTPUT
# =========================
print("\n===== MODEL PERFORMANCE =====")

print("\n--- Error Metrics ---")
print(f"MAE           : {mae:.3f}%") # Mean Absolute Error
print(f"RMSE          : {rmse:.3f}%") # Root Mean square Error
print(f"R² Score      : {r2:.3f}")

print("\n--- Prediction Accuracy ---")
print(f"Tolerance Acc : {tol_accuracy:.2%} (±{tolerance}%)")
print(f"Direction Acc : {direction_acc:.2%}")

print("\n--- Trading Metrics (Important) ---")
print(f"Target Hit Rate        : {hit_rate:.2%}")
print(f"Adjusted Hit Rate (80%): {adjusted_hit_rate:.2%}")
print(f"Avg Overshoot         : {avg_overshoot:.3f}%")
print(f"Avg Miss              : {avg_miss:.3f}%")

