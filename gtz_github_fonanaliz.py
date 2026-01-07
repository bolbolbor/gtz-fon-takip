#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions (FonAnaliz Sayfası)
Direkt FonAnaliz sayfasından veri çeker
"""

import requests
import os
import re
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')
FON_KODU = "GTZ"
FON_URL = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={FON_KODU}"


def telegram_mesaj_gonder(mesaj):
    """Telegram mesajı gönderir"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False


def fonanaliz_sayfasi_cek():
    """FonAnaliz sayfasından HTML çeker ve parse eder"""
    print(f"\n📡 FonAnaliz sayfası çekiliyor...")
    print(f"🔗 {FON_URL}")
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.tefas.gov.tr/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    session.headers.update(headers)
    
    try:
        # Önce ana sayfaya git (cookie için)
        print("🍪 Cookie alınıyor...")
        session.get("https://www.tefas.gov.tr/", verify=False, timeout=10)
        
        # Biraz bekle
        import time
        time.sleep(2)
        
        # FonAnaliz sayfasını çek
        print("📄 FonAnaliz sayfası isteniyor...")
        response = session.get(FON_URL, verify=False, timeout=15)
        
        print(f"📨 HTTP Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Response Length: {len(response.text)} bytes")
        
        # HTML kontrolü
        if "erişim engellendi" in response.text.lower() or "access denied" in response.text.lower():
            print("❌ Erişim engellendi (WAF)")
            return None
        
        # Fiyat bul - HTML'den regex ile
        print("\n🔍 HTML'den fiyat aranıyor...")
        
        # Virgüllü sayıları bul (5,123456 formatında)
        pattern = r'\b\d{1,2}[.,]\d{3,10}\b'
        matches = re.findall(pattern, response.text)
        
        print(f"📊 Bulunan sayılar: {len(matches)}")
        
        fiyat = None
        for match in matches[:20]:  # İlk 20 tanesini kontrol et
            try:
                # Türkçe formatı düzelt
                temiz = match.replace('.', '').replace(',', '.')
                f = float(temiz)
                
                # GTZ için mantıklı fiyat aralığı
                if 0.1 < f < 1000:
                    print(f"  💰 Olası fiyat: {f:.6f} TL (orijinal: {match})")
                    
                    if not fiyat:
                        fiyat = f
                        print(f"✅ Fiyat seçildi: {fiyat:.6f} TL")
                        
            except:
                continue
        
        if fiyat:
            return {
                'fiyat': fiyat,
                'tarih': datetime.now().strftime('%d.%m.%Y'),
                'kaynak': 'FonAnaliz HTML Parse'
            }
        else:
            print("❌ Fiyat bulunamadı!")
            
            # İlk 1000 karakteri göster
            print("\n📄 Sayfa içeriği (ilk 1000 karakter):")
            print(response.text[:1000])
            
            return None
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def main():
    print("="*70)
    print(f"🔍 GTZ FON KONTROLÜ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Telegram kontrol
    print(f"🔑 Telegram Token: {'✅ Var' if TELEGRAM_TOKEN else '❌ YOK'}")
    print(f"🔑 Chat ID: {'✅ Var' if CHAT_ID else '❌ YOK'}")
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("\n❌ GitHub Secrets eksik!")
        return
    
    # Test mesajı
    telegram_mesaj_gonder(
        f"🔍 <b>GTZ Kontrol (FonAnaliz)</b>\n\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
        f"🤖 GitHub Actions"
    )
    
    # Veri çek
    veri = fonanaliz_sayfasi_cek()
    
    if veri:
        print(f"\n✅ BAŞARILI!")
        print(f"💰 Fiyat: {veri['fiyat']:.6f} TL")
        print(f"📅 Tarih: {veri['tarih']}")
        print(f"🌐 Kaynak: {veri['kaynak']}")
        
        mesaj = (
            f"✅ <b>GTZ Veri Alındı!</b>\n\n"
            f"💰 Fiyat: <b>{veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {veri['tarih']}\n"
            f"🌐 {veri['kaynak']}\n\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
            f"🤖 GitHub Actions"
        )
        telegram_mesaj_gonder(mesaj)
    else:
        print("\n❌ Veri alınamadı!")
        telegram_mesaj_gonder(
            "❌ <b>GTZ - Veri Alınamadı</b>\n\n"
            "FonAnaliz sayfasından veri çekilemedi.\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
    
    print("="*70)


if __name__ == "__main__":
    main()
