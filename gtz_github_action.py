#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions (Debug Versiyonu)
Response içeriğini gösterir
"""

import requests
import os
import json
from datetime import datetime
import urllib3

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
    """TEFAS'tan fon verisini çeker"""
    print("📡 TEFAS'a bağlanılıyor...")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    
    # Önce ana sayfaya git
    referer_url = "https://www.tefas.gov.tr/TarihselVeriler.aspx"
    try:
        session.get(referer_url, verify=False, timeout=10)
        print("✅ Cookie alındı")
    except Exception as e:
        print(f"⚠️ Cookie hatası: {e}")
    
    session.headers.update({
        "Referer": referer_url,
        "Origin": "https://www.tefas.gov.tr"
    })
    
    api_url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    bugun = datetime.now().strftime('%Y-%m-%d')
    
    data = {
        "fontip": "ALL",
        "bastarih": bugun,
        "bittarih": bugun,
        "fonkod": FON_KODU
    }
    
    try:
        print(f"📊 İstek gönderiliyor...")
        print(f"📅 Tarih: {bugun}")
        print(f"🔗 URL: {api_url}")
        
        response = session.post(api_url, data=data, timeout=25, verify=False)
        
        print(f"📨 HTTP Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Response Length: {len(response.text)} bytes")
        
        # Response içeriğini göster
        print(f"\n📄 Response İlk 1000 Karakter:")
        print("="*70)
        print(response.text[:1000])
        print("="*70)
        
        # HTML kontrolü
        if "<html" in response.text.lower() or "<!doctype" in response.text.lower():
            print("\n⚠️ HTML response alındı - WAF veya hata sayfası olabilir")
            
            # Telegram'a gönder
            telegram_mesaj_gonder(
                "⚠️ <b>HTML Response Alındı</b>\n\n"
                f"İlk 500 karakter:\n<code>{response.text[:500]}</code>"
            )
            return None
        
        # JSON parse dene
        result = response.json()
        
        if result and len(result) > 0:
            veri = result[0]
            print(f"\n✅ JSON parse başarılı!")
            print(f"💰 Fiyat: {veri.get('FIYAT', 0)}")
            
            return {
                'fiyat': float(veri.get('FIYAT', 0)),
                'tarih': veri.get('TARIH', ''),
                'kisi': veri.get('KISISAYISI', 0),
                'portfoy': float(veri.get('PORTFOYBUYUKLUK', 0))
            }
        else:
            print("❌ Boş result")
            return None
            
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON Parse Hatası: {e}")
        print(f"Response metni Telegram'a gönderiliyor...")
        
        # Tam response'u Telegram'a gönder
        telegram_mesaj_gonder(
            f"❌ <b>JSON Parse Hatası</b>\n\n"
            f"Status: {response.status_code}\n"
            f"Content-Type: {response.headers.get('Content-Type', 'N/A')}\n\n"
            f"İlk 800 karakter:\n<code>{response.text[:800]}</code>"
        )
        return None
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def main():
    print("="*70)
    print(f"🔍 GTZ DEBUG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Secrets eksik!")
        return
    
    # Test mesajı
    telegram_mesaj_gonder(
        f"🔍 <b>GTZ Debug Başladı</b>\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )
    
    # Fon verisi
    veri = tefas_fon_al()
    
    if veri:
        print(f"\n✅ BAŞARILI!")
        mesaj = (
            f"✅ <b>GTZ Başarılı!</b>\n\n"
            f"💰 Fiyat: <b>{veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {veri['tarih']}\n"
            f"👥 Yatırımcı: {veri['kisi']:,}\n"
            f"💼 Portföy: {veri['portfoy']:,.2f} TL"
        )
        telegram_mesaj_gonder(mesaj)
    else:
        print("\n❌ Veri alınamadı!")
    
    print("="*70)


if __name__ == "__main__":
    main()
