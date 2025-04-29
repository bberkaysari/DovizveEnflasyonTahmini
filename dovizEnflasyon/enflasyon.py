import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import matplotlib.pyplot as plt

# 1. Veriyi Yükleme
# ';' ile ayrılmış CSV dosyasını yükleyelim
df = pd.read_csv('//gelişmeler/tufe.csv        ', sep=';')
df.columns = ['Tarih', 'Değer']  # Sütun adlarını uygun şekilde yeniden adlandıralım

# 2. Veri Ön İşleme
# Tarih sütununu datetime formatına dönüştürme ve yıl, ay olarak ayırma
df['Tarih'] = pd.to_datetime(df['Tarih'], format='%B.%Y')  # Örneğin: January.2005
df['Yıl'] = df['Tarih'].dt.year
df['Ay'] = df['Tarih'].dt.month

# Eksik değerleri kaldırma
df = df.dropna()

# 'Tarih' sütununu kaldırma
df = df.drop(columns=['Tarih'])

# 3. Özellik ve Hedef Değişken Belirleme
X = df[['Yıl', 'Ay']]
y = df['Değer']

# Eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Hiperparametre Optimizasyonu için GridSearchCV Ayarları
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.05, 0.1, 0.2],
    'max_depth': [3, 5, 7],
    'subsample': [0.8, 1]
}

xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)

# GridSearchCV ile en iyi hiperparametreleri bulma
grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1)
grid_search.fit(X_train, y_train)

# En iyi hiperparametreleri alalım
best_params = grid_search.best_params_
print("En İyi Hiperparametreler:", best_params)

# 5. En İyi Model ile Tahmin
best_model = grid_search.best_estimator_

# Test veri seti üzerinden tahmin yapma
y_pred = best_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error (MSE): {mse}")

# 6. Gelecekteki Enflasyon Değerlerini Tahmin Etme (2024 için)
future_dates = pd.DataFrame({
    'Yıl': [2024]*12,
    'Ay': list(range(1, 13))
})

future_pred = best_model.predict(future_dates)

# Konsola tahmin edilen enflasyon değerlerini yazdırma
print("Model 2 2024 Yılı Tahmini Enflasyon Değerleri:")
for month, prediction in zip(future_dates['Ay'], future_pred):
    print(f"{month}.Ay: %{prediction:.2f}")

# 7. Sonuçları Görselleştirme
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Değer'], label='Gerçek Değerler')
plt.plot(range(len(df), len(df) + 12), future_pred, label='2024 Tahminleri', color='red')
plt.xlabel("Zaman")
plt.ylabel("TÜFE Değeri")
plt.title("Türkiye 2005 İtibariyle TÜİK Enflasyon Grafiği Ve 2024 Yılı Tahmini (Model 2) ")
plt.legend()
plt.show()
