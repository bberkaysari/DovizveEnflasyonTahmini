from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from io import StringIO
import requests
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import os
import json

app = Flask(__name__)
CORS(app)

# Global cache for storing data and models
data_cache = {}
model_cache = {}

@app.route('/forecast', methods=['POST'])
def forecast():
    data = request.json
    selected_currency = data.get('currency', 'USD')
    frequency = data.get('frequency', '1')
    start_date = data.get('start_date', None)
    end_date = data.get('end_date', None)

    currencies = ['USD', 'EUR']

    for currency in currencies:
        if currency not in data_cache:
            series = f"TP.DK.{currency}.S.YTL"
            startDate = "01-01-2019"
            endDate = "23-12-2024"
            typee = "csv"
            aggregationTypes = "avg"
            formulas = "0"

            url = (
                f"https://evds2.tcmb.gov.tr/service/evds/series={series}"
                f"&startDate={startDate}&endDate={endDate}&type={typee}"
                f"&aggregationTypes={aggregationTypes}&formulas={formulas}&frequency={frequency}"
            )

            headers = {
                "User-Agent": "Mozilla/5.0",
                "key": "QIP7s50SVj"
            }

            response = requests.get(url, headers=headers, verify=False)
            if response.status_code != 200:
                return jsonify({"error": f"API request failed for {currency}", "status": response.status_code})

            csv_data = StringIO(response.text)
            data = pd.read_csv(csv_data)

            if "UNIXTIME" in data.columns:
                data.drop(columns=["UNIXTIME"], inplace=True)

            try:
                data["Tarih"] = pd.to_datetime(data["Tarih"], format="%d-%m-%Y", errors="coerce")
            except Exception as e:
                return jsonify({"error": f"Date parsing failed for {currency}", "message": str(e)})

            data.dropna(subset=["Tarih"], inplace=True)
            data.set_index("Tarih", inplace=True)
            column_name = series.replace(".", "_")
            data.rename(columns={column_name: f"{currency}_Kuru"}, inplace=True)

            if frequency == "1":
                data = data.asfreq("D")
            else:
                data = data.asfreq("ME")

            if data.empty:
                return jsonify({"error": f"No data available for {currency}"})

            data_cache[currency] = data

    if selected_currency not in model_cache:
        data = data_cache[selected_currency]
        p, d, q = 1, 1, 1
        P, D, Q, s = 1, 1, 1, 12 if frequency == "0" else 30

        model = SARIMAX(data[f"{selected_currency}_Kuru"], order=(p, d, q), seasonal_order=(P, D, Q, s))
        sarima_fit = model.fit(disp=False)
        model_cache[selected_currency] = sarima_fit

    sarima_fit = model_cache[selected_currency]
    data = data_cache[selected_currency]

    if frequency == "1":
        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date must be provided for daily forecasts."})

        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
        except Exception as e:
            return jsonify({"error": "Invalid date format.", "message": str(e)})

        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        forecast = sarima_fit.get_prediction(start=date_range[0], end=date_range[-1])
        forecast_values = forecast.predicted_mean.tolist()
        confidence_intervals = forecast.conf_int().values.tolist()

        results = {
            "dates": date_range.strftime("%Y-%m-%d").tolist(),
            "forecast": forecast_values,
            "conf_intervals": confidence_intervals,
            "type": "currency"
        }

    else:
        future_dates = pd.date_range(start=data.index[-1] + pd.offsets.MonthBegin(1), periods=12, freq="M")
        forecast = sarima_fit.get_forecast(steps=12)
        forecast_values = forecast.predicted_mean.tolist()
        confidence_intervals = forecast.conf_int().values.tolist()

        results = {
            "dates": future_dates.strftime("%Y-%m").tolist(),
            "forecast": forecast_values,
            "conf_intervals": confidence_intervals,
            "type": "currency"
        }

    return jsonify(results)

@app.route('/inflation', methods=['POST'])
def inflation_forecast():
    try:
        df = pd.read_csv('tufe.csv', sep=';')
        df.columns = ['Tarih', 'Değer']
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%B.%Y')
        df['Yıl'] = df['Tarih'].dt.year
        df['Ay'] = df['Tarih'].dt.month
        df = df.dropna()
        df = df.drop(columns=['Tarih'])

        X = df[['Yıl', 'Ay']]
        y = df['Değer']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        param_grid = {'n_estimators': [100, 200], 'learning_rate': [0.05, 0.1, 0.2], 'max_depth': [3, 5, 7], 'subsample': [0.8, 1]}
        xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
        grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1)
        grid_search.fit(X_train, y_train)

        future_dates = pd.DataFrame({'Yıl': [2024] * 12, 'Ay': list(range(1, 13))})
        future_pred = grid_search.best_estimator_.predict(future_dates)

        future_pred = [float(pred) for pred in future_pred]

        results = {
            "dates": [f"2024-{str(month).zfill(2)}" for month in future_dates['Ay']],
            "forecast": future_pred,
            "type": "inflation"
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": "An error occurre  d during inflation forecast", "message": str(e)}), 500

@app.route("/forecast_static", methods=["GET"])
def forecast_static():
    if not os.path.exists("tahmin.json"):
        return jsonify({"error": "Tahmin verisi mevcut değil. Lütfen model çalıştırılsın."}), 500
    with open("tahmin.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)