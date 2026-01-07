#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEFAS API Test - BindFonKarsilastirma
GitHub Actions'tan bu API'ye erişilip erişilemediğini test eder
"""

import requests
import os
import json
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')


def telegram_mesaj_gonder(mesaj):
    """Telegram mesajı gönderir"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False


def test_api(api_url, api_name, method="GET", data=None):
    """API'yi test eder"""
    print(f"\n{'='*70}")
    print(f"🔍 TEST: {api_name}")
    print(f"{'='*70}")
    print(f"🔗 URL: {api_url}")
    print(f"📋 Method: {method}")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9"
    })
    
    # Önce ana sayfaya git
    try:
        session.get("https://www.tefas.gov.tr/", verify=False, timeout=10)
        print("✅ Cookie alındı")
    except Exception as e:
        print(f"⚠️ Cookie hatası: {e}")
    
    session.headers.update({
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx"
    })
    
    try:
        if method == "POST":
            response = session.post(api_url, data=data, timeout=25, verify=False)
        else:
            response = session.get(api_url, timeout=25, verify=False)
        
        print(f"📨 HTTP Status: {response.status_code}")
        print(f"📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Response Length: {len(response.text)} bytes")
        
        # İlk 500 karakter
        print(f"\n📄 Response İlk 500 Karakter:")
        print("-"*70)
        print(response.text[:500])
        print("-"*70)
        
        # HTML kontrolü
        is_html = "<html" in response.text.lower() or "<!doctype" in response.text.lower()
        is_blocked = "erişim engellendi" in response.text.lower() or "access denied" in response.text.lower()
        
        if is_html:
            if is_blocked:
                result = "❌ ERİŞİM ENGELLENDİ (WAF)"
                emoji = "🚫"
            else:
                result = "⚠️ HTML response (hata sayfası olabilir)"
                emoji = "⚠️"
        else:
            try:
                json_data = response.json()
                result = f"✅ BAŞARILI - JSON alındı ({len(json_data)} item)"
                emoji = "✅"
            except:
                result = "⚠️ JSON değil ama HTML de değil"
                emoji = "⚠️"
        
        print(f"\n{emoji} Sonuç: {result}\n")
        
        return {
            "api": api_name,
            "url": api_url,
            "status": response.status_code,
            "is_html": is_html,
            "is_blocked": is_blocked,
            "result": result,
            "emoji": emoji,
            "response_preview": response.text[:300]
        }
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return {
            "api": api_name,
            "url": api_url,
            "error": str(e),
            "result": f"❌ İstek hatası: {e}",
            "emoji": "❌"
        }


def main():
    print("="*70)
    print(f"🧪 TEFAS API TEST SÜİTİ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    # Test 1: BindFonKarsilastirma
    result1 = test_api(
        "https://www.tefas.gov.tr/api/DB/BindFonKarsilastirma",
        "BindFonKarsilastirma",
        method="POST",
        data={"fontip": "YAT"}
    )
    results.append(result1)
    
    # Test 2: BindHistoryInfo (bildiğimiz engellenen)
    result2 = test_api(
        "https://www.tefas.gov.tr/api/DB/BindHistoryInfo",
        "BindHistoryInfo",
        method="POST",
        data={
            "fontip": "ALL",
            "bastarih": "2026-01-07",
            "bittarih": "2026-01-07",
            "fonkod": "GTZ"
        }
    )
    results.append(result2)
    
    # Test 3: BindHistoryAllInfo (başka endpoint)
    result3 = test_api(
        "https://www.tefas.gov.tr/api/DB/BindHistoryAllInfo",
        "BindHistoryAllInfo",
        method="POST",
        data={"fonkod": "GTZ"}
    )
    results.append(result3)
    
    # Özet
    print("\n" + "="*70)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("="*70)
    
    mesaj_parts = ["🧪 <b>TEFAS API Test Sonuçları</b>\n"]
    
    for result in results:
        print(f"{result['emoji']} {result['api']}: {result.get('status', 'N/A')}")
        mesaj_parts.append(f"{result['emoji']} <b>{result['api']}</b>")
        mesaj_parts.append(f"   Status: {result.get('status', 'Hata')}")
        
        if result.get('is_blocked'):
            mesaj_parts.append(f"   ❌ ERİŞİM ENGELLİ")
        elif result.get('is_html'):
            mesaj_parts.append(f"   ⚠️ HTML response")
        elif 'error' not in result:
            mesaj_parts.append(f"   ✅ Erişilebilir")
        
        mesaj_parts.append("")
    
    # Telegram'a gönder
    if TELEGRAM_TOKEN and CHAT_ID:
        telegram_mesaj_gonder("\n".join(mesaj_parts))
    
    print("="*70)


if __name__ == "__main__":
    main()
