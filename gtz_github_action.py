#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - Debug Versiyonu
TEFAS bağlantısını detaylı test eder
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
    except Exception as e:
        print(f"Telegram hatası: {e}")
        return False


def tefas_test_1():
    """TEFAS API Test 1 - Direkt bağlantı"""
    print("\n--- TEST 1: TEFAS Direkt Bağlantı ---")
    url = f"https://www.tefas.gov.tr/api/DB/BindHistoryInfo?fonkod={FON_KODU}"
    
    try:
        print(f"URL: {url}")
        response = requests.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Items: {len(data)}")
            if data:
                print(f"İlk veri: {data[0]}")
                return data[0]
        return None
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {e}")
        return None


def tefas_test_2():
    """TEFAS API Test 2 - User Agent ile"""
    print("\n--- TEST 2: User Agent ile ---")
    url = f"https://www.tefas.gov.tr/api/DB/BindHistoryInfo?fonkod={FON_KODU}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Items: {len(data)}")
            if data:
                return data[0]
        return None
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {e}")
        return None


def tefas_test_3():
    """TEFAS API Test 3 - Tam headers"""
    print("\n--- TEST 3: Tam Headers ---")
    url = f"https://www.tefas.gov.tr/api/DB/BindHistoryInfo?fonkod={FON_KODU}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.tefas.gov.tr/',
        'Origin': 'https://www.tefas.gov.tr'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Items: {len(data)}")
            if data:
                return data[0]
        return None
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {e}")
        return None


def tefas_test_4():
    """TEFAS API Test 4 - Alternatif URL"""
    print("\n--- TEST 4: Alternatif API Endpoint ---")
    url = f"https://ws.tefas.gov.tr/PortfolioValuations/api/DB/BindHistoryInfo?fonkod={FON_KODU}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Items: {len(data)}")
            if data:
                return data[0]
        return None
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {e}")
        return None


def main():
    print("="*70)
    print(f"🔍 TEFAS BAĞLANTI DEBUG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    sonuclar = []
    
    # Test 1
    veri1 = tefas_test_1()
    sonuclar.append(("Test 1 - Direkt", veri1 is not None))
    
    # Test 2
    veri2 = tefas_test_2()
    sonuclar.append(("Test 2 - User Agent", veri2 is not None))
    
    # Test 3
    veri3 = tefas_test_3()
    sonuclar.append(("Test 3 - Tam Headers", veri3 is not None))
    
    # Test 4
    veri4 = tefas_test_4()
    sonuclar.append(("Test 4 - Alt. Endpoint", veri4 is not None))
    
    print("\n" + "="*70)
    print("📊 SONUÇLAR:")
    print("="*70)
    
    mesaj_parts = ["🔍 <b>TEFAS Bağlantı Test Sonuçları</b>\n"]
    
    for test_adi, basarili in sonuclar:
        emoji = "✅" if basarili else "❌"
        durum = "BAŞARILI" if basarili else "BAŞARISIZ"
        print(f"{emoji} {test_adi}: {durum}")
        mesaj_parts.append(f"{emoji} {test_adi}: {durum}")
    
    # Başarılı olan veriyi kullan
    basarili_veri = veri1 or veri2 or veri3 or veri4
    
    if basarili_veri:
        fiyat = float(basarili_veri.get('FIYAT', 0))
        tarih = basarili_veri.get('TARIH', '')
        
        print(f"\n💰 FON BİLGİSİ:")
        print(f"   Fiyat: {fiyat:.6f} TL")
        print(f"   Tarih: {tarih}")
        
        mesaj_parts.append(f"\n💰 <b>GTZ Bilgisi Alındı!</b>")
        mesaj_parts.append(f"Fiyat: {fiyat:.6f} TL")
        mesaj_parts.append(f"Tarih: {tarih}")
    else:
        print("\n❌ TÜM TESTLER BAŞARISIZ!")
        mesaj_parts.append(f"\n❌ <b>Tüm testler başarısız!</b>")
        mesaj_parts.append(f"GitHub Actions'tan TEFAS'a erişilemiyor")
    
    print("="*70)
    
    # Telegram'a gönder
    telegram_mesaj_gonder("\n".join(mesaj_parts))


if __name__ == "__main__":
    main()
