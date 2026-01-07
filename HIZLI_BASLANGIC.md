# 🚀 HIZLI BAŞLANGIÇ - GTZ FON TAKİP SİSTEMİ

## 📦 İndirdiğiniz Dosyalar

```
gtz-fon-takip/
├── .github/
│   └── workflows/
│       └── fon-takip.yml          # GitHub Actions otomatik çalıştırma dosyası
├── gtz_github_action.py            # Ana fon takip scripti (GitHub için)
├── gtz_fon_takip.py               # Alternatif: Local bilgisayarda çalıştırma
├── test_sistem.py                 # Test scripti
├── README.md                      # Genel bilgi
├── GITHUB_KURULUM.md              # Detaylı GitHub kurulum rehberi
├── KULLANIM_REHBERI.md            # Local kullanım rehberi
└── .gitignore                     # Git ignore dosyası
```

---

## ⚡ 3 ADIMDA KURULUM

### 1️⃣ GitHub'da Repository Oluşturun

1. https://github.com → **Sign up** (veya Login)
2. Sağ üstten **"+ New repository"**
3. İsim: `gtz-fon-takip`
4. **Public** seçin
5. ✅ **Add a README** işaretleyin
6. **Create repository**

### 2️⃣ Dosyaları Yükleyin

**Kolay Yöntem (Sürükle-Bırak):**
1. Repository'de **"Add file" → "Upload files"**
2. Tüm dosyaları sürükleyip bırakın
3. **"Commit changes"**

**ÖNEMLİ:** `.github/workflows/fon-takip.yml` için:
- Repository ana sayfasında **"Create new file"** tıklayın
- Dosya adı: `.github/workflows/fon-takip.yml`
- `fon-takip.yml` içeriğini kopyala-yapıştır
- **"Commit"**

### 3️⃣ Secrets Ekleyin

1. Repository → **Settings**
2. Sol menü → **Secrets and variables** → **Actions**
3. **"New repository secret"** (2 tane ekleyin):

**Secret 1:**
```
Name: TELEGRAM_TOKEN
Value: 8228813125:AAGlCKIYXlYFvve-NNBrZNIGgKCfuXEMOeY
```

**Secret 2:**
```
Name: CHAT_ID  
Value: 1432624195
```

---

## ✅ TEST EDİN

1. **Actions** sekmesi
2. **"GTZ Fon Takip"** seçin
3. **"Run workflow"** → **"Run workflow"**
4. 30 saniye bekleyin
5. Telegram'dan mesaj geldi mi kontrol edin! 📱

---

## 🎉 TAMAMLANDI!

Artık sistem:
- ✅ Her 5 dakikada otomatik çalışıyor
- ✅ GTZ fon değişikliklerini takip ediyor
- ✅ Telegram'dan bildirim gönderiyor
- ✅ 24/7 aktif (GitHub sunucularında)
- ✅ Tamamen ücretsiz!

---

## 📱 Nasıl Çalıştığını Görün

**Actions** sekmesinde her çalıştırmanın loglarını görebilirsiniz:
- Yeşil ✅ = Başarılı
- Sarı 🟡 = Çalışıyor
- Kırmızı ❌ = Hata var

---

## 🛠️ Sorun mu Var?

### Workflow çalışmıyor
→ **Actions** sekmesinde **"Enable workflow"** yapın

### Telegram mesajı gelmiyor
→ Secrets'ı kontrol edin (TELEGRAM_TOKEN ve CHAT_ID)

### Detaylı yardım
→ `GITHUB_KURULUM.md` dosyasını okuyun

---

## 💡 İPUCU

İlk test mesajını aldıktan sonra, sistem otomatik olarak her 5 dakikada bir çalışacak. 

Fon fiyatı değiştiğinde otomatik olarak Telegram'dan bildirim alacaksınız! 🔔

---

**Başarılar! 🚀**
