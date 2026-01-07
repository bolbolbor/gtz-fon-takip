#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTZ Fon Takip - Sadece Değişiklik Bildirimi
Fiyat değişince Telegram'a bildirir
"""

import requests
import os
import re
import json
from datetime import datetime
import urllib3
from html.parser import HTMLParser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
CHAT_ID = os.environ.get('CHAT_ID', '')
FON_KODU = "GTZ"
FON_URL = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={FON_KODU}"
VERI_DOSYASI = "gtz_son_deger.json"


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
        
        if ',' in text and len(text) < 20:
            pattern = r'\d{1,3}[.,]\d{3,10}'
            matches = re.findall(pattern, text)
            
            for match in matches:
                try:
                    temiz = match.replace('.', '').replace(',', '.')
                    fiyat = float(temiz)
                    
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
        session.get("https://www.tefas.gov.tr/", verify=False, timeout=10)
        
        import time
        time.sleep(2)
        
        # FonAnaliz sayfası
        response = session.get(FON_URL, verify=False, timeout=15)
        
        print(f"📨 HTTP Status: {response.status_code}")
        
        if "erişim engellendi" in response.text.lower():
            print("❌ Erişim engellendi")
            return None
        
        # HTML Parser
        parser = TEFASHTMLParser()
        parser.feed(response.text)
        
        print(f"📊 {len(parser.fiyatlar)} olası fiyat bulundu")
        
        # Fiyat seç
        fiyat = None
        
        # ID/Class kontrolü
        for f in parser.fiyatlar:
            id_str = str(f['id']).lower()
            class_str = str(f['class']).lower()
            
            if any(keyword in id_str + class_str for keyword in ['price', 'fiyat', 'value', 'deger']):
                fiyat = f['deger']
                print(f"✅ Fiyat bulundu: {fiyat:.6f} TL")
                break
        
        # Ondalık uzunluğuna göre
        if not fiyat and parser.fiyatlar:
            benzersiz = {}
            for f in parser.fiyatlar:
                if f['deger'] not in benzersiz:
                    benzersiz[f['deger']] = f
            
            for deger, f in benzersiz.items():
                ondalik = str(deger).split('.')[1] if '.' in str(deger) else ''
                if len(ondalik) >= 4:
                    fiyat = deger
                    print(f"✅ Fiyat bulundu: {fiyat:.6f} TL")
                    break
        
        if fiyat:
            return {
                'fiyat': fiyat,
                'tarih': datetime.now().strftime('%d.%m.%Y'),
                'zaman': datetime.now().strftime('%H:%M:%S')
            }
        else:
            print("❌ Fiyat bulunamadı")
            return None
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def son_degeri_oku():
    """GitHub'dan son değeri okur"""
    try:
        with open(VERI_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("📝 İlk çalıştırma - veri dosyası yok")
        return None
    except Exception as e:
        print(f"⚠️ Dosya okuma hatası: {e}")
        return None


def son_degeri_kaydet(veri):
    """Son değeri dosyaya kaydeder"""
    try:
        with open(VERI_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        print(f"💾 Veri kaydedildi: {veri['fiyat']:.6f} TL")
        return True
    except Exception as e:
        print(f"⚠️ Dosya kaydetme hatası: {e}")
        return False


def main():
    print("="*70)
    print(f"🔍 GTZ KONTROL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Telegram secrets eksik!")
        return
    
    # Güncel veriyi çek (sessiz)
    guncel_veri = fonanaliz_sayfasi_cek()
    
    if not guncel_veri:
        print("\n❌ Veri alınamadı!")
        return
    
    print(f"\n✅ Güncel fiyat: {guncel_veri['fiyat']:.6f} TL")
    
    # Önceki veriyi oku
    son_veri = son_degeri_oku()
    
    if son_veri is None:
        # İlk çalıştırma
        print("\n📝 İLK ÇALIŞTIRMA")
        print("Başlangıç değeri kaydediliyor...")
        
        son_degeri_kaydet(guncel_veri)
        
        mesaj = (
            f"🚀 <b>GTZ Fon Takip Başlatıldı!</b>\n\n"
            f"💰 Başlangıç Fiyatı: <b>{guncel_veri['fiyat']:.6f} TL</b>\n"
            f"📅 Tarih: {guncel_veri['tarih']}\n"
            f"⏰ Saat: {guncel_veri['zaman']}\n\n"
            f"🔔 Fiyat değiştiğinde bildirim gelecek"
        )
        telegram_mesaj_gonder(mesaj)
        
        print("✅ Başlangıç mesajı gönderildi")
        
    else:
        # Karşılaştırma
        print(f"🔍 Önceki fiyat: {son_veri['fiyat']:.6f} TL")
        print(f"🔍 Güncel fiyat: {guncel_veri['fiyat']:.6f} TL")
        
        if guncel_veri['fiyat'] != son_veri['fiyat']:
            # DEĞİŞİKLİK VAR!
            fark = guncel_veri['fiyat'] - son_veri['fiyat']
            yuzde = (fark / son_veri['fiyat']) * 100
            
            if fark > 0:
                yon = "📈 YUKARI"
                emoji = "🟢"
            else:
                yon = "📉 AŞAĞI"
                emoji = "🔴"
            
            print(f"\n{emoji} DEĞİŞİKLİK TESPİT EDİLDİ!")
            print(f"   Fark: {fark:+.6f} TL ({yuzde:+.2f}%)")
            
            # Telegram mesajı
            mesaj = (
                f"{emoji} <b>GTZ FİYAT DEĞİŞTİ!</b>\n\n"
                f"{yon}\n\n"
                f"💰 Önceki: {son_veri['fiyat']:.6f} TL\n"
                f"💰 Yeni: <b>{guncel_veri['fiyat']:.6f} TL</b>\n\n"
                f"📊 Fark: <b>{fark:+.6f} TL</b>\n"
                f"📊 Değişim: <b>{yuzde:+.2f}%</b>\n\n"
                f"📅 {guncel_veri['tarih']}\n"
                f"⏰ {guncel_veri['zaman']}"
            )
            telegram_mesaj_gonder(mesaj)
            
            print("✅ Değişiklik bildirimi gönderildi")
            
            # Yeni değeri kaydet
            son_degeri_kaydet(guncel_veri)
            
        else:
            # Değişiklik yok
            print("\n✅ Fiyat aynı - Bildirim gönderilmedi")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
