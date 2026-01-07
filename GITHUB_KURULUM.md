# 🚀 GTZ FON TAKİP - GITHUB ACTIONS KURULUM REHBERİ

## 📋 Gereksinimler
- GitHub hesabı (ücretsiz)
- Telegram Bot Token ve Chat ID (zaten var ✅)

---

## 🎯 ADIM ADIM KURULUM

### 1️⃣ GitHub Hesabı Oluşturun (Eğer yoksa)

1. https://github.com adresine gidin
2. **Sign up** butonuna tıklayın
3. Email, kullanıcı adı ve şifre ile kayıt olun
4. Email'inizi doğrulayın

---

### 2️⃣ Yeni Repository (Depo) Oluşturun

1. GitHub'a giriş yapın
2. Sağ üst köşeden **"+"** işaretine tıklayın
3. **"New repository"** seçin
4. Repository ayarları:
   - **Repository name**: `gtz-fon-takip` (veya istediğiniz bir isim)
   - **Description**: "GTZ Fon Takip Sistemi"
   - **Public** veya **Private** seçin (ikisi de çalışır)
   - ✅ **Add a README file** kutusunu işaretleyin
5. **Create repository** butonuna tıklayın

---

### 3️⃣ Dosyaları Yükleyin

Repository oluşturduktan sonra:

1. **"Add file"** → **"Upload files"** seçin

2. Şu dosyaları sürükleyip bırakın:
   - `gtz_github_action.py`
   - `.github/workflows/fon-takip.yml`

   **DİKKAT:** `.github/workflows/fon-takip.yml` dosyası için:
   - Önce `.github` klasörü oluşturun
   - İçinde `workflows` klasörü oluşturun
   - `fon-takip.yml` dosyasını buraya koyun

3. **"Commit changes"** butonuna tıklayın

**VEYA Komut Satırından:**

```bash
# Klasör yapısını oluşturun
mkdir -p .github/workflows

# Dosyaları kopyalayın
# gtz_github_action.py dosyasını ana klasöre
# fon-takip.yml dosyasını .github/workflows/ içine

# Git işlemleri
git init
git add .
git commit -m "İlk commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/gtz-fon-takip.git
git push -u origin main
```

---

### 4️⃣ GitHub Secrets Ekleyin (ÖNEMLİ!)

Repository sayfasında:

1. **Settings** sekmesine gidin
2. Sol menüden **"Secrets and variables"** → **"Actions"** seçin
3. **"New repository secret"** butonuna tıklayın

**İki tane secret ekleyin:**

**Secret 1:**
- **Name**: `TELEGRAM_TOKEN`
- **Value**: `8228813125:AAGlCKIYXlYFvve-NNBrZNIGgKCfuXEMOeY`
- **"Add secret"** butonuna tıklayın

**Secret 2:**
- **Name**: `CHAT_ID`
- **Value**: `1432624195`
- **"Add secret"** butonuna tıklayın

---

### 5️⃣ GitHub Actions'ı Aktifleştirin

1. Repository sayfasında **"Actions"** sekmesine gidin
2. **"I understand my workflows, go ahead and enable them"** butonuna tıklayın
3. Sol menüden **"GTZ Fon Takip"** workflow'unu seçin
4. **"Enable workflow"** butonuna tıklayın (eğer görünüyorsa)

---

### 6️⃣ İlk Testi Yapın (Manuel)

1. **"Actions"** sekmesinde
2. Sol menüden **"GTZ Fon Takip"** seçin
3. Sağ tarafta **"Run workflow"** butonuna tıklayın
4. Yeşil **"Run workflow"** butonuna tekrar tıklayın
5. Birkaç saniye sonra workflow başlayacak
6. Workflow'a tıklayarak logları görebilirsiniz
7. Telegram'dan mesaj gelip gelmediğini kontrol edin!

---

## ✅ KURULUM TAMAMLANDI!

Artık sistem:
- ✅ Her 5 dakikada bir otomatik çalışacak
- ✅ TEFAS'tan GTZ fon değerini kontrol edecek
- ✅ Değişiklik olduğunda Telegram'dan bildirim gönderecek
- ✅ 24/7 aktif olacak (GitHub serverlarında)
- ✅ Tamamen ücretsiz!

---

## 📊 Nasıl Çalışır?

```
Her 5 Dakika
    ↓
GitHub Actions Başlar
    ↓
TEFAS'tan Fon Değerini Çeker
    ↓
Önceki Değer ile Karşılaştırır
    ↓
Değişiklik Var mı?
    ├─ Evet → Telegram Mesajı Gönder
    └─ Hayır → Hiçbir şey yapma
    ↓
5 Dakika Bekle
    ↓
Tekrar Et
```

---

## 🔍 Logları Görüntüleme

1. GitHub repository'nizde **"Actions"** sekmesine gidin
2. Son çalıştırmaları göreceksiniz
3. Herhangi birine tıklayarak detaylı logları görebilirsiniz

---

## ⚙️ Özelleştirme

### Kontrol Süresini Değiştirmek:

`.github/workflows/fon-takip.yml` dosyasında:

```yaml
schedule:
  - cron: '*/5 * * * *'  # Her 5 dakika
```

Diğer seçenekler:
- `*/10 * * * *` = Her 10 dakika
- `*/15 * * * *` = Her 15 dakika
- `*/30 * * * *` = Her 30 dakika
- `0 * * * *` = Her saat başı
- `0 9-17 * * 1-5` = Hafta içi 09:00-17:00 arası her saat

**NOT:** GitHub Actions minimum 5 dakika destekler.

---

## 🛠️ Sorun Giderme

### Workflow çalışmıyor:
- Actions sekmesinde aktif mi kontrol edin
- Secrets doğru mu kontrol edin
- Repository Public mu kontrol edin (Private'da da çalışır ama GitHub hesabı verified olmalı)

### Telegram mesajı gelmiyor:
- Secrets'ı doğru girdiğinizden emin olun
- Bot token ve chat ID'yi tekrar kontrol edin
- Actions loglarından hata mesajlarını kontrol edin

### TEFAS verisi gelmiyor:
- TEFAS mesai saatleri dışında veri güncellemez
- Hafta sonu ve tatil günleri çalışmaz
- Actions loglarından detaylı hata mesajını görebilirsiniz

---

## 📝 Notlar

- ✅ **Tamamen ücretsiz**
- ✅ **Herhangi bir sunucu gerektirmez**
- ✅ **Bilgisayarınız kapalı olsa bile çalışır**
- ⚠️ **GitHub Actions ücretsiz limiti: Ayda 2000 dakika** (bu sistem için fazlasıyla yeterli)
- ⚠️ **Fon fiyatları sadece iş günlerinde güncellenir**

---

## 🎉 Tebrikler!

Artık profesyonel bir fon takip sisteminiz var ve GitHub'ın sunucularında 24/7 çalışıyor! 🚀

Sorularınız varsa GitHub Issues'tan veya Telegram botunuzdan geri bildirim yapabilirsiniz.
