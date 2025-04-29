import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import requests
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# Döviz Tahmini için Fonksiyon
def fx_forecast():
    # Alpha Vantage API anahtarı
    api_key = '9HH2FH02TUCO914L'

    # Geçmiş döviz verilerini çeken yardımcı fonksiyon
    def get_historical_fx_data(base_currency, target_currency):
        url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={target_currency}&to_symbol={base_currency}&apikey={api_key}&outputsize=full'
        response = requests.get(url)
        if response.status_code != 200:
            return None  # API çağrısı başarısızsa None döndür
        try:
            data = response.json()  # JSON verilerini çözümle
        except requests.exceptions.JSONDecodeError:
            return None
        rates = data.get("Time Series FX (Daily)", {})  # Günlük döviz verilerini al
        if not rates:
            return None
        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame([(datetime.strptime(date, '%Y-%m-%d'), float(values['4. close']))
                           for date, values in rates.items()], columns=['Date', f'Rate_{target_currency}'])
        df = df.sort_values('Date').reset_index(drop=True)  # Tarihe göre sırala
        return df

    # USD ve EUR verilerini API'den çek
    usd_data = get_historical_fx_data('TRY', 'USD')
    eur_data = get_historical_fx_data('TRY', 'EUR')

    if usd_data is not None and eur_data is not None:
        # USD ve EUR verilerini birleştir
        df = usd_data.merge(eur_data, on='Date', how='inner')
        df.set_index('Date', inplace=True)  # Tarih sütununu indeks olarak ayarla
        df_diff = df.diff().dropna()  # Fark yöntemiyle verileri stabilize et

        # Kayar pencere yöntemiyle veri hazırlama
        window_size = 10
        X, y_usd, y_eur = [], [], []
        for i in range(window_size, len(df_diff)):
            X.append(df_diff.iloc[i - window_size:i].values.flatten())
            y_usd.append(df_diff['Rate_USD'].iloc[i])
            y_eur.append(df_diff['Rate_EUR'].iloc[i])

        X = np.array(X)
        y_usd = np.array(y_usd)
        y_eur = np.array(y_eur)

        # Veri setini eğitim ve test olarak ayır
        X_train_usd, X_test_usd, y_train_usd, y_test_usd = train_test_split(X, y_usd, test_size=0.2, random_state=42)
        X_train_eur, X_test_eur, y_train_eur, y_test_eur = train_test_split(X, y_eur, test_size=0.2, random_state=42)

        # XGBoost modellerini oluştur ve eğit
        model_usd = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.05, max_depth=6)
        model_usd.fit(X_train_usd, y_train_usd)

        model_eur = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.05, max_depth=6)
        model_eur.fit(X_train_eur, y_train_eur)

        # Gelecek 12 ay için tahmin yap
        future_preds_usd, future_preds_eur = [], []
        last_window_usd = X[-1]
        last_window_eur = X[-1]

        for _ in range(12):
            pred_usd = model_usd.predict(last_window_usd.reshape(1, -1))[0]
            pred_eur = model_eur.predict(last_window_eur.reshape(1, -1))[0]
            future_preds_usd.append(pred_usd)
            future_preds_eur.append(pred_eur)
            last_window_usd = np.roll(last_window_usd, -1)
            last_window_usd[-1] = pred_usd
            last_window_eur = np.roll(last_window_eur, -1)
            last_window_eur[-1] = pred_eur

        # Kümülatif toplamlarla tahmin edilen değerleri gerçek değerlere dönüştür
        future_pred_usd = np.cumsum(future_preds_usd) + df['Rate_USD'].iloc[-1]
        future_pred_eur = np.cumsum(future_preds_eur) + df['Rate_EUR'].iloc[-1]

        # Sonuçları bir pencere ve grafikle göster
        result_window("Döviz Kuru Tahmini", future_pred_usd, future_pred_eur, "Döviz Kuru")

        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['Rate_USD'], label='Gerçek USD/TRY')
        plt.plot(df.index, df['Rate_EUR'], label='Gerçek EUR/TRY')
        future_dates = [df.index[-1] + timedelta(days=30 * i) for i in range(1, 13)]
        plt.plot(future_dates, future_pred_usd, linestyle='--', label='Tahmin USD/TRY')
        plt.plot(future_dates, future_pred_eur, linestyle='--', label='Tahmin EUR/TRY')
        plt.legend()
        plt.title("TRY'nin Döviz Tahmini")
        plt.show()


# Enflasyon Tahmini için Fonksiyon
def inflation_forecast():
    # TÜFE verilerini CSV dosyasından yükle
    df = pd.read_csv('/Users/yusagca/Downloads/tufe.csv', sep=';')
    df.columns = ['Tarih', 'Değer']
    df['Tarih'] = pd.to_datetime(df['Tarih'], format='%B.%Y')  # Tarih formatını dönüştür
    df['Yıl'] = df['Tarih'].dt.year
    df['Ay'] = df['Tarih'].dt.month
    df = df.dropna()  # Eksik verileri çıkar
    df = df.drop(columns=['Tarih'])

    # Özellikler ve hedef değer
    X = df[['Yıl', 'Ay']]
    y = df['Değer']

    # Eğitim ve test setlerini ayır
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # XGBoost için hiperparametre arama
    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 1]
    }
    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
    grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error',
                               verbose=1)
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    # Gelecek 12 ayın tahminlerini yap
    future_dates = pd.DataFrame({
        'Yıl': [2024] * 12,
        'Ay': list(range(1, 13))
    })
    future_pred = best_model.predict(future_dates)

    # Sonuçları bir pencere ve grafikle göster
    result_window("Enflasyon Tahmini", future_pred, None, "Enflasyon")

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(df)), y, label='Gerçek TÜFE Değerleri', color='blue')
    plt.plot(range(len(df), len(df) + 12), future_pred, label='2024 Tahminleri', color='red')
    plt.xlabel("Zaman")
    plt.ylabel("TÜFE Değeri")
    plt.title("Türkiye TÜFE Verileri ve 2024 Tahminleri")
    plt.legend()
    plt.show()


# Konsol Çıktılarını Yeni Bir Pencerede Gösterme
def result_window(title, usd=None, eur=None, data_type="Döviz Kuru"):
    # Yeni bir Tkinter penceresi oluştur
    new_window = tk.Toplevel(root)
    new_window.title(title)
    text = ScrolledText(new_window, wrap=tk.WORD, width=60, height=20)
    text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Tahmin sonuçlarını göster
    if data_type == "Döviz Kuru":
        text.insert(tk.END, "Gelecek 12 Ay için Tahmini Döviz Kurları:\n")
        for month in range(12):
            text.insert(tk.END, f"{month + 1}. Ay:\n")
            text.insert(tk.END, f"  USD/TRY: {usd[month]:.2f}\n")
            text.insert(tk.END, f"  EUR/TRY: {eur[month]:.2f}\n\n")
    else:
        text.insert(tk.END, "Gelecek 12 Ay için Tahmini Enflasyon Değerleri:\n")
        for month in range(12):
            text.insert(tk.END, f"{month + 1}. Ay: %{usd[month]:.2f}\n")


# Tkinter Arayüzü
root = tk.Tk()
root.title("Tahmin Uygulaması")
root.geometry("600x500")

# Ana ekran başlığı
label = tk.Label(root, text="Tahmin Türünü Seçiniz:", font=("Arial", 16))
label.pack(pady=20)

# Döviz tahmini butonu
btn_fx = tk.Button(root, text="Döviz Kuru Tahmini", font=("Arial", 16), command=fx_forecast, width=20, height=10)
btn_fx.pack(pady=15)

# Enflasyon tahmini butonu
btn_inflation = tk.Button(root, text="Enflasyon Tahmini", font=("Arial", 16), command=inflation_forecast, width=20,
                          height=10)
btn_inflation.pack(pady=15)

# Tkinter ana döngüsü
root.mainloop()
