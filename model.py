import requests
import pandas as pd
import numpy as np
import json
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO
from datetime import datetime, timedelta
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_currency_data(series_code):
    startDate = "01-01-2021"
    endDate = datetime.now().strftime("%d-%m-%Y")

    url = (
        f"https://evds2.tcmb.gov.tr/service/evds/series={series_code}"
        f"&startDate={startDate}&endDate={endDate}&type=csv"
        f"&aggregationTypes=avg&formulas=0&frequency=1"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "key": os.getenv("EVDS_API_KEY")
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"❌ Veri alınamadı: {series_code} (HTTP {response.status_code})")
        return []

    df = pd.read_csv(StringIO(response.text)).dropna()
    df.set_index("Tarih", inplace=True)
    df.rename(columns={series_code.replace(".", "_"): "Kur"}, inplace=True)
    df.index = pd.to_datetime(df.index, format="%d-%m-%Y")

    model = SARIMAX(df["Kur"], order=(1,1,1), seasonal_order=(1,1,1,30))
    result = model.fit(disp=False)

    steps = 90
    future_dates = pd.date_range(df.index[-1] + timedelta(days=1), periods=steps, freq="D")
    forecast = result.get_forecast(steps=steps)
    pred = forecast.predicted_mean
    conf_int = forecast.conf_int()

    return [
        {
            "date": date.strftime("%Y-%m-%d"),
            "prediction": round(float(pred[i]), 4),
            "conf_low": round(float(conf_int.iloc[i, 0]), 4),
            "conf_high": round(float(conf_int.iloc[i, 1]), 4)
        }
        for i, date in enumerate(future_dates)
    ]

if __name__ == "__main__":
    print("🌍 USD verisi işleniyor...")
    usd_forecast = fetch_currency_data("TP.DK.USD.S.YTL")

    print("🌍 EUR verisi işleniyor...")
    eur_forecast = fetch_currency_data("TP.DK.EUR.S.YTL")

    all_forecasts = {
        "USD": usd_forecast,
        "EUR": eur_forecast
    }

    with open("tahmin.json", "w", encoding="utf-8") as f:
        json.dump(all_forecasts, f, ensure_ascii=False, indent=2)

    print("✅ tahmin.json başarıyla oluşturuldu.")



