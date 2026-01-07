#!/usr/bin/env bash
# GTZ Fon Takip - GitHub Actions (Bash Versiyon)
set -euo pipefail

# Ayarlar
FON_KODU="GTZ"
TELEGRAM_TOKEN="${TELEGRAM_TOKEN:-}"
CHAT_ID="${CHAT_ID:-}"
VERI_DOSYASI="gtz_last_value.txt"

# Tarih
BUGUN=$(date +%Y-%m-%d)

# TEFAS API
API_URL="https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
REFERER_URL="https://www.tefas.gov.tr/TarihselVeriler.aspx"

echo "============================================================"
echo "🔍 GTZ FON TAKİP - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# Telegram fonksiyonu
telegram_gonder() {
    local mesaj="$1"
    
    if [[ -z "$TELEGRAM_TOKEN" || -z "$CHAT_ID" ]]; then
        echo "❌ Telegram bilgileri eksik!"
        return 1
    fi
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${mesaj}" \
        -d "parse_mode=HTML" >/dev/null
    
    echo "✅ Telegram mesajı gönderildi"
}

# TEFAS'tan veri çek
echo ""
echo "📡 TEFAS'a bağlanılıyor..."

# Geçici cookie dosyası
COOKIES_FILE=$(mktemp)

# 1. Cookie alma
curl -s -c "$COOKIES_FILE" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "$REFERER_URL" >/dev/null

echo "✅ Cookie alındı"

# WAF bypass için bekleme
sleep 1

# 2. Veri çekme
echo "📊 Veri çekiliyor: $BUGUN"

RESPONSE=$(curl -s -b "$COOKIES_FILE" -X POST "$API_URL" \
  -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
  -H "Origin: https://www.tefas.gov.tr" \
  -H "Referer: $REFERER_URL" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --data "fontip=ALL&bastarih=$BUGUN&bittarih=$BUGUN&fonkod=$FON_KODU")

# Cookie dosyasını temizle
rm -f "$COOKIES_FILE"

# Response kontrolü
if ! echo "$RESPONSE" | jq empty >/dev/null 2>&1; then
    echo "❌ Geçersiz response!"
    echo ""
    echo "Response ilk 500 karakter:"
    echo "$RESPONSE" | head -c 500
    
    telegram_gonder "❌ GTZ - Geçersiz Response%0A%0ATEFAS bağlantı hatası%0A$(date '+%H:%M:%S')"
    exit 1
fi

# Veriyi parse et
FIYAT=$(echo "$RESPONSE" | jq -r '.[0].FIYAT // empty')
TARIH=$(echo "$RESPONSE" | jq -r '.[0].TARIH // empty')
KISI_SAYISI=$(echo "$RESPONSE" | jq -r '.[0].KISISAYISI // empty')
PORTFOY=$(echo "$RESPONSE" | jq -r '.[0].PORTFOYBUYUKLUK // empty')

if [[ -z "$FIYAT" ]]; then
    echo "❌ Veri bulunamadı!"
    telegram_gonder "❌ GTZ - Veri Bulunamadı%0A%0A$(date '+%H:%M:%S')"
    exit 1
fi

echo "✅ Veri alındı!"
echo "💰 Fiyat: $FIYAT TL"
echo "📅 Tarih: $TARIH"
echo "👥 Yatırımcı: $KISI_SAYISI"
echo "💼 Portföy: $PORTFOY TL"

# Önceki değeri oku
if [[ -f "$VERI_DOSYASI" ]]; then
    ONCEKI_FIYAT=$(cat "$VERI_DOSYASI")
else
    # İlk çalıştırma
    echo "$FIYAT" > "$VERI_DOSYASI"
    
    MESAJ="🚀 GTZ Fon Takip Başlatıldı!%0A%0A"
    MESAJ+="💰 Başlangıç Fiyatı: ${FIYAT} TL%0A"
    MESAJ+="📅 Tarih: ${TARIH}%0A"
    MESAJ+="👥 Yatırımcı: ${KISI_SAYISI}%0A%0A"
    MESAJ+="🤖 GitHub Actions (Bash)%0A"
    MESAJ+="⏰ $(date '+%H:%M:%S')"
    
    telegram_gonder "$MESAJ"
    
    echo ""
    echo "📝 İlk veri kaydedildi"
    exit 0
fi

# Değişiklik kontrolü
if [[ "$FIYAT" != "$ONCEKI_FIYAT" ]]; then
    echo ""
    echo "🔔 DEĞİŞİKLİK TESPİT EDİLDİ!"
    echo "   Önceki: $ONCEKI_FIYAT TL"
    echo "   Yeni: $FIYAT TL"
    
    # Fark hesapla (bc ile)
    FARK=$(echo "$FIYAT - $ONCEKI_FIYAT" | bc)
    YUZDE=$(echo "scale=2; ($FARK / $ONCEKI_FIYAT) * 100" | bc)
    
    # Yön belirle
    if (( $(echo "$FARK > 0" | bc -l) )); then
        YON="📈 YUKARI"
        EMOJI="🟢"
        FARK_STR="+${FARK}"
        YUZDE_STR="+${YUZDE}"
    else
        YON="📉 AŞAĞI"
        EMOJI="🔴"
        FARK_STR="${FARK}"
        YUZDE_STR="${YUZDE}"
    fi
    
    echo "   Fark: $FARK_STR TL ($YUZDE_STR%)"
    echo "   Yön: $YON"
    
    # Telegram mesajı
    MESAJ="${EMOJI} GTZ DEĞİŞTİ! ${YON}%0A%0A"
    MESAJ+="💰 Önceki: ${ONCEKI_FIYAT} TL%0A"
    MESAJ+="💰 Yeni: ${FIYAT} TL%0A%0A"
    MESAJ+="📊 Fark: ${FARK_STR} TL%0A"
    MESAJ+="📊 Değişim: ${YUZDE_STR}%%%0A%0A"
    MESAJ+="📅 ${TARIH}%0A"
    MESAJ+="⏰ $(date '+%H:%M:%S')%0A"
    MESAJ+="🤖 GitHub Actions"
    
    telegram_gonder "$MESAJ"
    
    # Yeni değeri kaydet
    echo "$FIYAT" > "$VERI_DOSYASI"
    
    # Git'e commit
    git config user.name "GitHub Actions Bot"
    git config user.email "actions@github.com"
    git add "$VERI_DOSYASI"
    git commit -m "🔄 GTZ fiyat güncellendi: $FIYAT TL" || true
    git push || true
    
    echo "✅ Yeni değer kaydedildi"
else
    echo ""
    echo "✅ Değişiklik yok"
fi

echo ""
echo "============================================================"
