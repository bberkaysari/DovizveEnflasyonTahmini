import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO
import urllib3

# InsecureRequestWarning uyarılarını bastırma
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_predict(currency="USD", frequency="1", forecast_steps=21):
    # EVDS API bilgileri
    series = f"TP.DK.{currency}.S.YTL"  # Dinamik döviz kuru serisi
    startDate = "01-01-2019"  # Başlangıç tarihi
    endDate = "23-12-2024"  # Bitiş tarihi
    typee = "csv"
    aggregationTypes = "avg"
    formulas = "0"

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
        data = pd.read_csv(csv_data)

        # İstenmeyen sütunları kaldırma
        if "UNIXTIME" in data.columns:
            data.drop(columns=["UNIXTIME"], inplace=True)

        # Tarih sütunundaki hatalı verileri belirleme
        try:
            data["Tarih"] = pd.to_datetime(data["Tarih"], format="%d-%m-%Y", errors="coerce")
        except Exception as e:
            print(f"Tarih formatı hatası: {e}")

        # Hatalı tarihleri kaldırma
        data.dropna(subset=["Tarih"], inplace=True)
        data.set_index("Tarih", inplace=True)

        column_name = series.replace(".", "_")
        data.rename(columns={column_name: f"{currency}_Kuru"}, inplace=True)

        # Frekans bilgisi ekleme
        if frequency == "1":
            data = data.asfreq("D")
        else:
            data = data.asfreq("ME")

        print(f"\nÇekilen Veriler ({currency}):")
        print(data.head())

        if data.empty:
            print(f"Uyarı: {currency} için çekilen veri seti boş! API parametrelerini kontrol edin.")
            return

        # SARIMA modeliyle eğitim
        # SARIMA(p, d, q)(P, D, Q, s): Mevsimsel ve trend parametreleri
        p, d, q = 1, 1, 1  # ARIMA trend parametreleri
        P, D, Q, s = 1, 1, 1, 12 if frequency == "0" else 30  # Mevsimsel parametreler

        # SARIMA modeli tanımlama ve eğitme
        model = SARIMAX(data[f"{currency}_Kuru"], order=(p, d, q), seasonal_order=(P, D, Q, s))
        sarima_fit = model.fit(disp=False)

        # Model özeti
        print(sarima_fit.summary())

        # Tahmin yapma
        future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_steps,
                                     freq="D" if frequency == "1" else "M")
        forecast = sarima_fit.get_forecast(steps=forecast_steps)
        forecast_values = forecast.predicted_mean
        confidence_intervals = forecast.conf_int()

        # Tahmin sonuçlarını görselleştirme
        plt.figure(figsize=(14, 7))
        plt.plot(data.index, data[f"{currency}_Kuru"], label="Gerçek Değerler")
        plt.plot(future_dates, forecast_values, label=f"Tahmin - {currency}", linestyle="--")
        plt.fill_between(future_dates, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1],
                         color='k', alpha=0.2, label="Güven Aralığı")
        plt.title(f"{currency} Kuru Tahminleri (SARIMA)")
        plt.xlabel("Tarih")
        plt.ylabel(f"{currency} Kuru (TL)")
        plt.legend()
        plt.grid()
        plt.show()

        # Tahmin sonuçlarını DataFrame'e dönüştürme
        forecast_df = pd.DataFrame({
            "Tarih": future_dates,
            "Tahmin": forecast_values,
            "Alt Güven Aralığı": confidence_intervals.iloc[:, 0],
            "Üst Güven Aralığı": confidence_intervals.iloc[:, 1],
        })
        forecast_df.set_index("Tarih", inplace=True)

        print(f"\nGelecek Tahminler ({currency}):")
        print(forecast_df)

        # Tahmin sonuçlarını kaydetme
        forecast_df.to_csv(f"sarima_{currency.lower()}_{'aylik' if frequency == '0' else 'gunluk'}_tahmin.csv")
        print(f"Tahmin sonuçları 'sarima_{currency.lower()}_{'aylik' if frequency == '0' else 'gunluk'}_tahmin.csv' dosyasına kaydedildi.")
    else:
        print(f"HTTP Hatası: {response.status_code}")
        print("Lütfen API anahtarınızı ve URL'yi kontrol edin.")

# Aylık ve Günlük Kullanım
fetch_and_predict("EUR", "1", 13)  # Aylık Euro tahmini
