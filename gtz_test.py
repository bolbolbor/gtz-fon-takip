#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions (Basit Versiyon)
TEFAS her gün bir kez güncellenir, o yüzden sadece günlük bildirim gönderir
"""

import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')
FON_KODU = "GTZ"


def telegram_mesaj_gonder(mesaj):
    """Telegram mesajı gönderir"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False


def tefas_fon_al():
    """TEFAS'tan fon verisini çeker"""
    url = f"https://www.tefas.gov.tr/api/DB/BindHistoryInfo?fonkod={FON_KODU}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    'fiyat': float(data[0].get('FIYAT', 0)),
                    'tarih': data[0].get('TARIH', ''),
                    'kisi': data[0].get('KISISAYISI', 0)
                }
    except:
        pass
    return None


def main():
    print("="*60)
    print(f"🔍 GTZ FON - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test: Telegram çalışıyor mu?
    print("\n📱 Telegram testi...")
    test_ok = telegram_mesaj_gonder(
        f"✅ <b>GTZ Fon Takip - Test</b>\n\n"
        f"Sistem çalışıyor!\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )
    
    if test_ok:
        print("✅ Telegram mesajı gönderildi!")
    else:
        print("❌ Telegram hatası!")
        print("Secrets kontrol edin:")
        print(f"  Token: {'✓' if TELEGRAM_TOKEN else '✗'}")
        print(f"  Chat ID: {'✓' if CHAT_ID else '✗'}")
        return
    
    # Fon verisini al
    print("\n📊 TEFAS'tan veri alınıyor...")
    veri = tefas_fon_al()
    
    if veri:
        print(f"✅ Başarılı!")
        print(f"💰 Fiyat: {veri['fiyat']:.6f} TL")
        print(f"📅 Tarih: {veri['tarih']}")
        
        mesaj = (
            f"📊 <b>GTZ Güncel Durum</b>\n\n"
            f"💰 Fiyat: <b>{veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {veri['tarih']}\n"
            f"👥 Yatırımcı: {veri['kisi']:,}\n\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
        telegram_mesaj_gonder(mesaj)
    else:
        print("❌ TEFAS'tan veri alınamadı!")
        telegram_mesaj_gonder("⚠️ <b>GTZ - Veri Alınamadı</b>\n\nTEFAS bağlantı hatası")
    
    print("="*60)


if __name__ == "__main__":
    main()
