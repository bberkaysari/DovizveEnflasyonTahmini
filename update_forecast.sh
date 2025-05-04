#!/bin/bash

# Ortamı yükle
source /Users/berkaysari/Desktop/dovizveenflasyon/.venv/bin/activate
cd /Users/berkaysari/Desktop/dovizveenflasyon

# JSON dosyalarını güncelle
python3 train_model.py

# Git ayarları
git config user.name "bberkaysari"
git config user.email "bberkaysari0@gmail.com"

# Değişiklikleri Git'e ekle, commit et ve pushla
git add tahmin.json enflasyon_tahmin.json
git commit -m "Otomatik güncelleme: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin dovizenflasyon