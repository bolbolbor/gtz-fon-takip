#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - GitHub Actions v2 (İyileştirilmiş HTML Parse)
"""

import requests
import os
import re
from datetime import datetime
import urllib3
from html.parser import HTMLParser

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


class TEFASHTMLParser(HTMLParser):
    """TEFAS HTML'inden fiyat çıkarır"""
    
    def __init__(self):
        super().__init__()
        self.fiyatlar = []
        self.current_tag = None
        self.current_attrs = {}
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = dict(attrs)
        
    def handle_data(self, data):
        text = data.strip()
        
        # Virgüllü sayıları bul
        if ',' in text and len(text) < 20:
            # Türkçe format: 5,123456 veya 5.123,456
            pattern = r'\d{1,3}[.,]\d{3,10}'
            matches = re.findall(pattern, text)
            
            for match in matches:
                try:
                    # Türkçe formatı düzelt
                    temiz = match.replace('.', '').replace(',', '.')
                    fiyat = float(temiz)
                    
                    # GTZ için mantıklı aralık
                    if 1 < fiyat < 100:
                        self.fiyatlar.append({
                            'deger': fiyat,
                            'orijinal': match,
                            'tag': self.current_tag,
                            'class': self.current_attrs.get('class', ''),
                            'id': self.current_attrs.get('id', '')
                        })
                except:
                    pass


def fonanaliz_sayfasi_cek():
    """FonAnaliz sayfasından veri çeker"""
    print(f"\n📡 FonAnaliz sayfası çekiliyor...")
    print(f"🔗 {FON_URL}")
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.tefas.gov.tr/",
    }
    
    session.headers.update(headers)
    
    try:
        # Cookie için ana sayfaya git
        print("🍪 Cookie alınıyor...")
        session.get("https://www.tefas.gov.tr/", verify=False, timeout=10)
        
        import time
        time.sleep(2)
        
        # FonAnaliz sayfası
        print("📄 FonAnaliz sayfası isteniyor...")
        response = session.get(FON_URL, verify=False, timeout=15)
        
        print(f"📨 HTTP Status: {response.status_code}")
        print(f"📏 Response Length: {len(response.text)} bytes")
        
        if "erişim engellendi" in response.text.lower():
            print("❌ Erişim engellendi (WAF)")
            return None
        
        # HTML Parser ile parse et
        print("\n🔍 HTML parse ediliyor...")
        parser = TEFASHTMLParser()
        parser.feed(response.text)
        
        print(f"📊 {len(parser.fiyatlar)} olası fiyat bulundu")
        
        # En uygun fiyatı seç
        fiyat = None
        
        # Önce ID/Class'a göre filtrele
        for f in parser.fiyatlar:
            id_str = str(f['id']).lower()
            class_str = str(f['class']).lower()
            
            # Fiyat ile ilgili ID/Class ara
            if any(keyword in id_str + class_str for keyword in ['price', 'fiyat', 'value', 'deger']):
                fiyat = f['deger']
                print(f"✅ ID/Class ile bulundu: {fiyat:.6f} TL")
                print(f"   Tag: {f['tag']}, ID: {f['id']}, Class: {f['class']}")
                break
        
        # Bulunamazsa en büyüğü al (genellikle ana fiyat daha büyük font'ta)
        if not fiyat and parser.fiyatlar:
            # Benzersiz değerleri al
            benzersiz_fiyatlar = {}
            for f in parser.fiyatlar:
                if f['deger'] not in benzersiz_fiyatlar:
                    benzersiz_fiyatlar[f['deger']] = f
            
            # İlk 5 benzersiz fiyatı göster
            print("\n📋 Bulunan benzersiz fiyatlar:")
            for i, (deger, f) in enumerate(list(benzersiz_fiyatlar.items())[:5]):
                print(f"  {i+1}. {deger:.6f} TL (orijinal: {f['orijinal']})")
            
            # En mantıklı olanı seç
            # Genellikle 4-6 haneli ondalıklı kısımlar ana fiyattır
            for deger, f in benzersiz_fiyatlar.items():
                ondalik_kisim = str(deger).split('.')[1] if '.' in str(deger) else ''
                if len(ondalik_kisim) >= 4:  # 4+ haneli ondalık
                    fiyat = deger
                    print(f"✅ Ondalık uzunluğuna göre seçildi: {fiyat:.6f} TL")
                    break
            
            # Hala bulunamadıysa ilk mantıklı olanı al
            if not fiyat:
                for deger in benzersiz_fiyatlar.keys():
                    if 1 < deger < 20:  # GTZ genelde bu aralıkta
                        fiyat = deger
                        print(f"✅ Aralığa göre seçildi: {fiyat:.6f} TL")
                        break
        
        if fiyat:
            return {
                'fiyat': fiyat,
                'tarih': datetime.now().strftime('%d.%m.%Y'),
                'kaynak': 'FonAnaliz HTML Parse v2'
            }
        else:
            print("❌ Fiyat seçilemedi!")
            
            # Simple regex deneme (yedek)
            print("\n🔄 Basit regex deneniyor...")
            pattern = r'\b[4-6][.,]\d{6}\b'  # GTZ genelde 4-6 ile başlar
            matches = re.findall(pattern, response.text)
            
            if matches:
                print(f"📊 Regex ile bulundu: {matches[:5]}")
                temiz = matches[0].replace(',', '.')
                fiyat = float(temiz)
                print(f"✅ Regex fiyatı: {fiyat:.6f} TL")
                
                return {
                    'fiyat': fiyat,
                    'tarih': datetime.now().strftime('%d.%m.%Y'),
                    'kaynak': 'FonAnaliz Regex'
                }
            
            return None
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def main():
    print("="*70)
    print(f"🔍 GTZ FON KONTROLÜ v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("\n❌ GitHub Secrets eksik!")
        return
    
    telegram_mesaj_gonder(
        f"🔍 <b>GTZ Kontrol v2</b>\n\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )
    
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
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
        telegram_mesaj_gonder(mesaj)
    else:
        print("\n❌ Veri alınamadı!")
        telegram_mesaj_gonder("❌ GTZ - Veri alınamadı")
    
    print("="*70)


if __name__ == "__main__":
    main()
