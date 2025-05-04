#!/bin/bash

# Ortamı yükle
source /Users/berkaysari/Desktop/dovizveenflasyon/.venv/bin/activate
cd /Users/berkaysari/Desktop/dovizveenflasyon

# JSON dosyalarını güncelle
python3 train_model.py

# Kur verisini de güncelle (eklenmiş satır)
python3 <<EOF
import requests
import json
from datetime import datetime

try:
    res = requests.get("https://api.frankfurter.app/latest?from=TRY&to=USD,EUR")
    data = res.json()
    usd = round(1 / data["rates"]["USD"], 4)
    eur = round(1 / data["rates"]["EUR"], 4)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("kur.json", "w", encoding="utf-8") as f:
        json.dump({"USD": usd, "EUR": eur, "updated_at": now}, f, ensure_ascii=False, indent=2)

    print("✅ kur.json güncellendi:", now)

except Exception as e:
    print("❌ Kur verisi alınamadı:", e)
EOF

# Git ayarları
git config user.name "bberkaysari"
git config user.email "bberkaysari0@gmail.com"

# Değişiklikleri Git'e ekle, commit et ve pushla
git add tahmin.json enflasyon_tahmin.json kur.json
git commit -m "Otomatik güncelleme: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin dovizenflasyon