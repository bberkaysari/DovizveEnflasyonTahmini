import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO

# EVDS API bilgileri
series = "TP.DK.EUR.S.YTL"  # Euro kuru serisi
startDate = "01-01-2021"  # Başlangıç tarihi
endDate = "23-12-2024"  # Bitiş tarihi
typee = "csv"
aggregationTypes = "avg"
formulas = "0"
frequency = "1"  # Günlük veri

# URL oluşturma
url = (
    f"https://evds2.tcmb.gov.tr/service/evds/series={series}"
    f"&startDate={startDate}&endDate={endDate}&type={typee}"
    f"&aggregationTypes={aggregationTypes}&formulas={formulas}&frequency={frequency}"
)

# HTTP Headers (key artık burada)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "key": "pgQUhmsXDd"  # API anahtarınızı buraya yazın
}

# Veri çekme
response = requests.get(url, headers=headers, verify=False)

if response.status_code == 200:
    # CSV verisini Pandas DataFrame'e çevirme
    csv_data = StringIO(response.text)
    euro = pd.read_csv(csv_data)
    euro.dropna(inplace=True)
    euro.set_index("Tarih", inplace=True)
    euro.rename(columns={series.replace(".", "_"): "Euro_Kuru"}, inplace=True)

    # Veriyi tarih formatına çevirme
    euro.index = pd.to_datetime(euro.index, format="%d-%m-%Y")
    print("Çekilen Veriler:")
    print(euro.head())

    # SARIMA modeliyle eğitim
    # SARIMA(p, d, q)(P, D, Q, s): Mevsimsel ve trend parametreleri
    p, d, q = 1, 1, 1  # ARIMA trend parametreleri
    P, D, Q, s = 1, 1, 1, 30  # Mevsimsel parametreler (s=30 günlük mevsimsellik)

    # SARIMA modeli tanımlama ve eğitme
    model = SARIMAX(euro["Euro_Kuru"], order=(p, d, q), seasonal_order=(P, D, Q, s))
    sarima_fit = model.fit(disp=False)

    # Model özeti
    print(sarima_fit.summary())

    # Tahmin yapma
    forecast_steps = 13  # 2024 Aralık ve 2025'in tüm ayları için tahmin
    future_dates = pd.date_range(start="2024-12-01", end="2025-12-31", freq="M")
    forecast = sarima_fit.get_forecast(steps=forecast_steps)
    forecast_index = future_dates
    forecast_values = forecast.predicted_mean
    confidence_intervals = forecast.conf_int()

    # Tahmin sonuçlarını görselleştirme
    plt.figure(figsize=(14, 7))
    plt.plot(euro.index, euro["Euro_Kuru"], label="Gerçek Değerler")
    plt.plot(forecast_index, forecast_values, label="Tahmin (2024 Aralık - 2025)", linestyle="--")
    plt.fill_between(forecast_index, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1],
                     color='k', alpha=0.2, label="Güven Aralığı")
    plt.title("Euro Kuru Tahminleri (SARIMA)")
    plt.xlabel("Tarih")
    plt.ylabel("Euro Kuru (TL)")
    plt.legend()
    plt.grid()
    plt.show()

    # Tahmin sonuçlarını DataFrame'e dönüştürme
    forecast_df = pd.DataFrame({
        "Tarih": forecast_index,
        "Tahmin": forecast_values,
        "Alt Güven Aralığı": confidence_intervals.iloc[:, 0],
        "Üst Güven Aralığı": confidence_intervals.iloc[:, 1],
    })
    forecast_df.set_index("Tarih", inplace=True)

    print("\nGelecek Tahminler:")
    print(forecast_df)

    # Tahmin sonuçlarını kaydetme
    forecast_df.to_csv("sarima_euro_tahmin_2024_2025.csv")
    print("Tahmin sonuçları 'sarima_euro_tahmin_2024_2025.csv' dosyasına kaydedildi.")
else:
    print(f"HTTP Hatası: {response.status_code}")
    print("Lütfen API anahtarınızı ve URL'yi kontrol edin.")
