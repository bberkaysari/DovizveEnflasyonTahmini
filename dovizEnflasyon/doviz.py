import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Load and clean the dataset
file_path = 'EVDS (1).xlsx'
evds_data = pd.ExcelFile(file_path)
evds_df = evds_data.parse('EVDS')

# Clean column names
evds_df.columns = evds_df.columns.str.strip().str.replace(' ', '_')
evds_df.rename(columns={
    'Tarih': 'Date',
    'TP_DK_USD_S_YTL': 'USD',
    'TP_DK_EUR_S_YTL': 'EUR'
}, inplace=True)

# Convert 'Date' to datetime format
evds_df['Date'] = pd.to_datetime(evds_df['Date'], format='%d-%m-%Y', errors='coerce')
evds_df.dropna(subset=['Date', 'USD', 'EUR'], inplace=True)

# Set 'Date' as the index
evds_df.set_index('Date', inplace=True)
evds_df['USD'] = pd.to_numeric(evds_df['USD'], errors='coerce')
evds_df['EUR'] = pd.to_numeric(evds_df['EUR'], errors='coerce')
evds_df.dropna(inplace=True)

# Filter data to exclude dates after 2024-01
evds_df = evds_df[evds_df.index < '2024-01-01']

# Resample data to monthly frequency
evds_monthly = evds_df.resample('M').mean()

# Calculate differences to make the data stationary
df_diff = evds_monthly.diff().dropna()

# Prepare the data for training
window_size = 12  # Using a 12-month window for predictions
X, y_usd, y_eur = [], [], []

for i in range(window_size, len(df_diff)):
    X.append(df_diff.iloc[i - window_size:i].values.flatten())
    y_usd.append(df_diff['USD'].iloc[i])
    y_eur.append(df_diff['EUR'].iloc[i])

X = np.array(X)
y_usd = np.array(y_usd)
y_eur = np.array(y_eur)

# Split the data into training and testing sets
X_train, X_test, y_train_usd, y_test_usd = train_test_split(X, y_usd, test_size=0.2, random_state=42)
_, _, y_train_eur, y_test_eur = train_test_split(X, y_eur, test_size=0.2, random_state=42)

# Train models
model_usd = XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.05, max_depth=6)
model_usd.fit(X_train, y_train_usd)

model_eur = XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.05, max_depth=6)
model_eur.fit(X_train, y_train_eur)

# Predict future values
future_preds_usd, future_preds_eur = [], []
last_window = df_diff.iloc[-window_size:].values.flatten()

for _ in range(12):  # Predict for 12 future months
    pred_usd = model_usd.predict(last_window.reshape(1, -1))[0]
    pred_eur = model_eur.predict(last_window.reshape(1, -1))[0]
    future_preds_usd.append(pred_usd)
    future_preds_eur.append(pred_eur)

    last_window = np.roll(last_window, -2)
    last_window[-2] = pred_usd
    last_window[-1] = pred_eur

# Convert predictions to original scale
future_pred_usd = np.cumsum(future_preds_usd) + evds_monthly['USD'].iloc[-1]
future_pred_eur = np.cumsum(future_preds_eur) + evds_monthly['EUR'].iloc[-1]

# Generate future dates
future_dates = pd.date_range(start='2024-01-01', periods=12, freq='M')

# Plot predictions
plt.figure(figsize=(14, 8))
plt.plot(evds_monthly.index, evds_monthly['USD'], label='Actual USD/TRY', color='blue')
plt.plot(evds_monthly.index, evds_monthly['EUR'], label='Actual EUR/TRY', color='green')
plt.plot(future_dates, future_pred_usd, label='Predicted USD/TRY', linestyle='--', color='blue')
plt.plot(future_dates, future_pred_eur, label='Predicted EUR/TRY', linestyle='--', color='green')

plt.xlabel('Date')
plt.ylabel('Exchange Rate (TRY)')
plt.title('Monthly Exchange Rate Prediction for USD and EUR')
plt.legend()
plt.grid()
plt.show()

# Print predictions
print("Predicted Monthly Values:")
for i, date in enumerate(future_dates):
    print(f"{date.strftime('%Y-%m')}:\n  USD Predicted: {future_pred_usd[i]:.2f}\n  EUR Predicted: {future_pred_eur[i]:.2f}\n")
