import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb

def inflation_forecast():
    df = pd.read_csv('/Users/yusagca/Downloads/tufe.csv', sep=';')
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

    return {f"2024-{month}": pred for month, pred in zip(future_dates['Ay'], future_pred)}

if __name__ == "__main__":
    print(inflation_forecast())
