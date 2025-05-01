import requests
import pandas as pd
import numpy as np
import json
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO
from datetime import datetime, timedelta
import os
import urllib3
from pytz import timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_forecast_with_real(series_code, label, steps=90):
    startDate = "01-01-2021"
    turkey_time = datetime.now(timezone("Europe/Istanbul"))
    endDate = turkey_time.strftime("%d-%m-%Y")

    url = (
        f"https://evds2.tcmb.gov.tr/service/evds/series={series_code}"
        f"&startDate={startDate}&endDate={endDate}&type=csv"
        f"&aggregationTypes=avg&formulas=0&frequency=1"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "key": os.getenv("EVDS_API_KEY")
    }

    print(f"🌐 {label} verisi çekiliyor...")
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"❌ {label} verisi alınamadı. HTTP {response.status_code}")
        return {"real": [], "forecast": []}

    df = pd.read_csv(StringIO(response.text)).dropna()
    df.set_index("Tarih", inplace=True)
    df.rename(columns={series_code.replace(".", "_"): "Kur"}, inplace=True)
    df.index = pd.to_datetime(df.index, format="%d-%m-%Y")

    # Gerçek veriler
    real_data = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "actual": round(float(value), 4)
        }
        for date, value in df["Kur"].items()
    ]

    print(f"⚙️ {label} modeli eğitiliyor...")
    model = SARIMAX(df["Kur"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 30))
    result = model.fit(disp=False)
    print(f"✅ {label} modeli eğitildi.")

    future = result.get_forecast(steps=steps)
    pred = future.predicted_mean.reset_index(drop=True)
    conf = future.conf_int().reset_index(drop=True)
    future_dates = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=steps, freq="D")

    forecast_data = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "prediction": round(float(pred[i]), 4),
            "conf_low": round(float(conf.iloc[i, 0]), 4),
            "conf_high": round(float(conf.iloc[i, 1]), 4)
        }
        for i, date in enumerate(future_dates)
    ]

    return {
        "real": real_data,
        "forecast": forecast_data
    }

# 🔮 USD ve EUR için geçmiş + tahmin verilerini al
usd = get_forecast_with_real("TP.DK.USD.S.YTL", "USD", steps=90)
eur = get_forecast_with_real("TP.DK.EUR.S.YTL", "EUR", steps=90)

turkey_now = datetime.now(timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")

output = {
    "generated_at": turkey_now,
    "forecast_days": 90,
    "forecasts": {
        "USD": {
            "real": usd["real"],
            "forecast": usd["forecast"]
        },
        "EUR": {
            "real": eur["real"],
            "forecast": eur["forecast"]
        }
    }
}

with open("tahmin.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("📁 tahmin.json başarıyla oluşturuldu.")