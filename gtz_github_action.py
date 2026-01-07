#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions (TEFAS Scraper Yöntemi)
Develooper1994'ün başarılı TEFAS erişim yöntemini kullanır
"""

import requests
import os
import json
from datetime import datetime
import urllib3

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """
    TEFAS'tan fon verisini çeker - develooper1994'ün yöntemi
    KEY POINT: Session + Referer + verify=False
    """
    print("📡 TEFAS'a bağlanılıyor...")
    
    # Session oluştur (cookie yönetimi için)
    session = requests.Session()
    
    # User-Agent ekle
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    # Önce ana sayfaya git (cookie almak için)
    referer_url = "https://www.tefas.gov.tr/TarihselVeriler.aspx"
    try:
        session.get(referer_url, verify=False, timeout=10)
        print("✅ Cookie alındı")
    except Exception as e:
        print(f"⚠️ Cookie alma hatası: {e}")
    
    # Referer ekle
    session.headers.update({"Referer": referer_url})
    
    # API isteği
    api_url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    
    # Bugünün tarihi
    bugun = datetime.now().strftime('%Y-%m-%d')
    
    data = {
        "fontip": "ALL",
        "bastarih": bugun,
        "bittarih": bugun,
        "fonkod": FON_KODU
    }
    
    try:
        print(f"📊 Veri isteniyor: {api_url}")
        print(f"📅 Tarih: {bugun}")
        
        response = session.post(api_url, data=data, timeout=25, verify=False)
        
        print(f"📨 HTTP Status: {response.status_code}")
        
        response.raise_for_status()
        
        # JSON parse
        result = response.json()
        
        if result and len(result) > 0:
            veri = result[0]
            print(f"✅ Veri alındı!")
            
            return {
                'fiyat': float(veri.get('FIYAT', 0)),
                'tarih': veri.get('TARIH', ''),
                'kisi': veri.get('KISISAYISI', 0),
                'portfoy': float(veri.get('PORTFOYBUYUKLUK', 0))
            }
        else:
            print("❌ Boş veri döndü")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request hatası: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        print(f"Response text: {response.text[:500]}")
        return None
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return None


def main():
    print("="*70)
    print(f"🔍 GTZ FON KONTROLÜ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Telegram kontrol
    print(f"\n🔑 Telegram Token: {'✅ Var' if TELEGRAM_TOKEN else '❌ YOK'}")
    print(f"🔑 Chat ID: {'✅ Var' if CHAT_ID else '❌ YOK'}")
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("\n❌ GitHub Secrets eksik!")
        return
    
    # Test mesajı
    print("\n📱 Test mesajı gönderiliyor...")
    test_ok = telegram_mesaj_gonder(
        f"🔍 <b>GTZ Kontrol Başladı</b>\n\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
        f"🤖 GitHub Actions (TEFAS Scraper Yöntemi)"
    )
    
    if test_ok:
        print("✅ Test mesajı gönderildi!")
    else:
        print("❌ Test mesajı gönderilemedi!")
    
    # Fon verisini al
    veri = tefas_fon_al()
    
    if veri:
        print(f"\n💰 BAŞARILI!")
        print(f"   Fiyat: {veri['fiyat']:.6f} TL")
        print(f"   Tarih: {veri['tarih']}")
        print(f"   Yatırımcı: {veri['kisi']:,}")
        print(f"   Portföy: {veri['portfoy']:,.2f} TL")
        
        mesaj = (
            f"✅ <b>GTZ Veri Alındı!</b>\n\n"
            f"💰 Fiyat: <b>{veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {veri['tarih']}\n"
            f"👥 Yatırımcı: {veri['kisi']:,}\n"
            f"💼 Portföy: {veri['portfoy']:,.2f} TL\n\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
            f"🤖 GitHub Actions"
        )
        telegram_mesaj_gonder(mesaj)
    else:
        print("\n❌ Veri alınamadı!")
        telegram_mesaj_gonder(
            "❌ <b>GTZ - Veri Alınamadı</b>\n\n"
            "TEFAS bağlantı hatası.\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
    
    print("="*70)


if __name__ == "__main__":
    main()
