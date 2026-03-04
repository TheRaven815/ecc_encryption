# Advanced ECC Cryptography Suite 🔐

Bu proje, **Elliptic Curve Cryptography (ECC)** protokollerini kullanarak güvenli anahtar üretimi, dijital imzalama ve doğrulama işlemlerini gerçekleştiren modern bir masaüstü uygulamasıdır. `customtkinter` ile geliştirilen şık ve karanlık mod destekli arayüzü sayesinde kriptografik işlemleri karmaşık komut satırları yerine kullanıcı dostu bir panel üzerinden yönetmenizi sağlar.

## ✨ Özellikler

- **Geniş Eğri Desteği:** 
  - NIST Eğrileri: SECP256R1 (P-256), SECP384R1 (P-384), SECP521R1 (P-521)
  - Modern Eğriler: Ed25519 (Dijital İmzalar için) ve X25519 (Anahtar Değişimi için)
- **Güvenli Anahtar Yönetimi:**
  - Parola korumalı (şifrelenmiş) özel anahtar (Private Key) üretimi.
  - Anahtarları `.pem` formatında dışa aktarma ve içe aktarma.
- **Dijital İmzalama:** Mesajlarınızı özel anahtarınızla imzalayarak bütünlüğünü ve kaynağını garanti altına alın.
- **İmza Doğrulama:** Paylaşılan genel anahtar (Public Key) ile imzaların geçerliliğini kontrol edin.
- **Modern UI:** Tamamen özelleştirilebilir, responsive ve karanlık mod uyumlu kullanıcı arayüzü.

## 🚀 Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/kullanici-adiniz/ecc_encryption.git
    cd ecc_encryption
    ```

2.  **Sanal Ortam Oluşturun (Önerilir):**
    ```bash
    python -m venv venv
    # Windows için:
    .\venv\Scripts\activate
    # Linux/Mac için:
    source venv/bin/activate
    ```

3.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

## 🛠 Kullanım

Uygulamayı başlatmak için ana dizinde şu komutu çalıştırın:

```bash
python ecc_generator.py
```

### Temel İş Akışı:
1.  **Anahtar Yönetimi:** Bir eğri seçin (örn: SECP256R1) ve "Generate New Keys" butonuna basın. İsterseniz anahtarlarınızı dosya olarak kaydedebilirsiniz.
2.  **İmzalama:** "Sign Message" sekmesine geçin, mesajınızı yazın ve "Sign Message with Private Key" butonuna tıklayarak Base64 formatında imzanızı oluşturun.
3.  **Doğrulama:** "Verify Signature" sekmesinde orijinal mesajı ve imzayı girerek genel anahtar ile doğruluğunu teyit edin.

## 📦 Gereksinimler

- Python 3.8+
- `cryptography`: Kriptografik işlemler için.
- `customtkinter`: Modern arayüz bileşenleri için.
- `darkdetect`: İşletim sistemi tema algılaması için.

## ⚠️ Güvenlik Uyarısı

Bu araç eğitim ve test amaçlıdır. Üretim (production) ortamlarında özel anahtarlarınızı (Private Key) asla paylaşmayın ve güvenli olmayan ortamlarda saklamayın.

---
*Bu proje modern kriptografi standartlarına (NIST, RFC 8032) uygun olarak geliştirilmiştir.*
