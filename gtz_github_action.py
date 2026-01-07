#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions Versiyonu
Her çalıştığında TEFAS'tan fon verisini kontrol eder ve değişiklik varsa bildirim gönderir
"""

import requests
import os
import json
from datetime import datetime

# Ortam değişkenlerinden al (GitHub Secrets'tan gelecek)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')

FON_KODU = "GTZ"
VERI_DOSYASI = "gtz_last_value.json"


def telegram_mesaj_gonder(mesaj):
    """Telegram üzerinden mesaj gönderir"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Telegram bilgileri eksik!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Mesaj gönderildi")
            return True
        else:
            print(f"❌ Mesaj gönderilemedi: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def tefas_fon_bilgisi_al(fon_kodu):
    """TEFAS'tan fon bilgisini çeker"""
    url = f"https://www.tefas.gov.tr/api/DB/BindHistoryInfo?fonkod={fon_kodu}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                son_veri = data[0]
                
                fon_bilgi = {
                    'fiyat': float(son_veri.get('FIYAT', 0)),
                    'tarih': son_veri.get('TARIH', ''),
                    'kisi_sayisi': son_veri.get('KISISAYISI', 0),
                    'portfoy_buyukluk': float(son_veri.get('PORTFOYBUYUKLUK', 0))
                }
                
                return fon_bilgi
            else:
                print("❌ Veri bulunamadı")
                return None
        else:
            print(f"❌ TEFAS'a bağlanılamadı: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def son_degeri_oku():
    """Son kaydedilen değeri okur"""
    try:
        if os.path.exists(VERI_DOSYASI):
            with open(VERI_DOSYASI, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"⚠️ Dosya okuma hatası: {e}")
        return None


def son_degeri_kaydet(veri):
    """Son değeri kaydeder"""
    try:
        with open(VERI_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        
        # Git'e commit et (GitHub Actions içinde)
        os.system('git config user.name "GitHub Actions Bot"')
        os.system('git config user.email "actions@github.com"')
        os.system(f'git add {VERI_DOSYASI}')
        os.system('git commit -m "🔄 Fon değeri güncellendi" || true')
        os.system('git push || true')
        
        return True
    except Exception as e:
        print(f"⚠️ Dosya kaydetme hatası: {e}")
        return False


def main():
    """Ana fonksiyon"""
    print("\n" + "="*60)
    print(f"🔍 GTZ FON KONTROLÜ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Güncel fon bilgisini al
    guncel_veri = tefas_fon_bilgisi_al(FON_KODU)
    
    if not guncel_veri:
        print("⚠️ Fon verisi alınamadı, işlem sonlandırılıyor")
        return
    
    print(f"💰 Güncel Fiyat: {guncel_veri['fiyat']:.6f} TL")
    print(f"📅 Tarih: {guncel_veri['tarih']}")
    
    # Son kaydedilen veriyi oku
    son_veri = son_degeri_oku()
    
    if son_veri is None:
        # İlk çalıştırma
        print("📝 İlk veri kaydediliyor...")
        son_degeri_kaydet(guncel_veri)
        
        mesaj = (
            f"🚀 <b>GTZ Fon Takip (GitHub Actions) Başlatıldı!</b>\n\n"
            f"📊 Fon: Garanti Portföy Gümüş Fon Sepeti\n"
            f"💰 İlk Fiyat: <b>{guncel_veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {guncel_veri['tarih']}\n"
            f"👥 Yatırımcı: {guncel_veri['kisi_sayisi']:,}\n"
            f"💼 Portföy: {guncel_veri['portfoy_buyukluk']:,.2f} TL\n\n"
            f"🤖 GitHub Actions ile 5 dakikada bir kontrol edilecek"
        )
        telegram_mesaj_gonder(mesaj)
        
    else:
        # Değişiklik kontrolü
        if guncel_veri['fiyat'] != son_veri['fiyat']:
            fark = guncel_veri['fiyat'] - son_veri['fiyat']
            yuzde = (fark / son_veri['fiyat']) * 100
            
            if fark > 0:
                yon = "📈 YUKARI"
                emoji = "🟢"
            else:
                yon = "📉 AŞAĞI"
                emoji = "🔴"
            
            print(f"{emoji} DEĞİŞİKLİK TESPİT EDİLDİ!")
            print(f"   Önceki: {son_veri['fiyat']:.6f} TL")
            print(f"   Yeni: {guncel_veri['fiyat']:.6f} TL")
            print(f"   Fark: {fark:+.6f} TL ({yuzde:+.2f}%)")
            
            # Telegram bildirimi gönder
            mesaj = (
                f"{emoji} <b>GTZ DEĞİŞTİ!</b> {yon}\n\n"
                f"💰 Önceki: {son_veri['fiyat']:.6f} TL\n"
                f"💰 Yeni: <b>{guncel_veri['fiyat']:.6f} TL</b>\n\n"
                f"📊 Fark: {fark:+.6f} TL\n"
                f"📊 Değişim: <b>{yuzde:+.2f}%</b>\n\n"
                f"📅 {guncel_veri['tarih']}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
                f"🤖 GitHub Actions"
            )
            telegram_mesaj_gonder(mesaj)
            
            # Yeni değeri kaydet
            son_degeri_kaydet(guncel_veri)
        else:
            print("✅ Değişiklik yok")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
