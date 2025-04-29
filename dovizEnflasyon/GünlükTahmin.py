import requests
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO
import sys
import warnings

warnings.filterwarnings("ignore")

def daily_forecast(start_date, end_date, series):
    # EVDS API bilgileri
    valid_series = {
        "dolar": "TP.DK.USD.S.YTL",
        "euro": "TP.DK.EUR.S.YTL"
    }
    if series not in valid_series:
        raise ValueError(f"Geçersiz series parametresi: {series}. Geçerli değerler: {list(valid_series.keys())}")

    series_code = valid_series[series]

    # URL oluşturma
    url = (
        f"https://evds2.tcmb.gov.tr/service/evds/series={series_code}"
        f"&startDate={start_date}&endDate={end_date}&type=csv"
        f"&aggregationTypes=avg&formulas=0&frequency=1"
    )
    print("oluşturulan url:",url)

    # HTTP Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "key": "pgQUhmsXDd"
    }

    # Veri çekme
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception(f"HTTP Hatası: {response.status_code}. Lütfen API anahtarınızı ve URL'yi kontrol edin.")

    # CSV verisini Pandas DataFrame'e çevirme
    csv_data = StringIO(response.text)
    data = pd.read_csv(csv_data)
    data.dropna(inplace=True)
    data.set_index("Tarih", inplace=True)
    data.rename(columns={series_code.replace(".", "_"): "Kur"}, inplace=True)
    data.index = pd.to_datetime(data.index, format="%d-%m-%Y")

    # SARIMA modeliyle eğitim
    model = SARIMAX(data["Kur"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 30))
    sarima_fit = model.fit(disp=False)

    # Tahmin yapma
    forecast_steps = 21  # 21 günlük tahmin
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_steps, freq="D")
    forecast = sarima_fit.get_forecast(steps=forecast_steps)
    forecast_values = forecast.predicted_mean
    confidence_intervals = forecast.conf_int()

    # Tahmin sonuçlarını DataFrame'e dönüştürme
    forecast_df = pd.DataFrame({
        "Tarih": future_dates,
        "Tahmin": forecast_values,
        "Alt Güven Aralığı": confidence_intervals.iloc[:, 0],
        "Üst Güven Aralığı": confidence_intervals.iloc[:, 1],
    })
    forecast_df.set_index("Tarih", inplace=True)
    print("tahminler",forecast_df)
    # Tahmin sonuçlarını döndürme
    return forecast_df

if __name__ == "__main__":
    # Komut satırından parametreleri al
    start_date = sys.argv[1]  # Başlangıç tarihi
    end_date = sys.argv[2]    # Bitiş tarihi
    series = sys.argv[3]      # Döviz türü (dolar veya euro)

    try:
        forecast_results = daily_forecast(start_date, end_date, series)
        # Tahmin sonuçlarını JSON formatında yazdır
        for date, row in forecast_results.iterrows():
            print(f"{date.strftime('%Y-%m-%d')} {row['Tahmin']:.4f}")
    except Exception as e:
        print(f"Hata: {e}")
