# ES YAŞAM - Proje Özel Kuralları ve Tercihleri

Bu dosya, Antigravity AI kodlama asistanının ES Yaşam projesinde her zaman hatırlaması gereken kurumsal bilgileri, tercihleri ve tasarım standartlarını içerir.

---

## 📞 Kurumsal ve Marka Bilgileri

*   **Marka Adı:** ES Yaşam
*   **Web Adresi:** `esyasam.com`
*   **Slogan:** "Daha güzel bir yaşam için"
*   **Ürün Grupları:** Temizlik ürünleri, kozmetik ürünler ve ev araç gereçleri.
*   **İlk Lansman Ürünleri:**
    1.  **Leke Çıkartıcı** (Viral temizlik ürünü)
    2.  **Sarı Güç** (Çok amaçlı temizleyici)
    3.  **Mavi Güç** (Ultra temizlik gücü)
*   **Kurumsal İletişim:** Kurumsal telefon veya WhatsApp iletişim numarası bulunmayacaktır. Bunun yerine yalnızca resmi Instagram hesabı olan **`@es_yasam`** (`https://instagram.com/es_yasam`) kullanılacaktır.

---

## 🌐 Depo ve Canlı Ortam Bilgileri

*   **GitHub Deposu:** `https://github.com/esyasam/shop` (Proje deposu bu bağlantıda saklanmaktadır).
*   **Canlı Ortam (Deployment):** **Cloudflare Pages** (`shop` projesi)
    *   **Hesap:** `Dyncher@gmail.com`
    *   **Canlı Alan Adı (Custom Domain):** `esyasam.com` (SSL Aktif)
    *   **Varsayılan Cloudflare Subdomain:** `shop-dhi.pages.dev`
    *   **Dağıtım Dalı (Production Branch):** `main` (Bu daldaki her güncelleme otomatik olarak canlıya dağıtılır).

---

## 🎨 Tasarım ve Görsel Arayüz Standartları

*   **Logo Dosyası:** `/public/images/logo.jpg` (Altın kabartmalı arma, zeytin dalları ve krem zeminli premium logo).
*   **Ana Renk Paleti (Logo ile Tam Uyumlu):**
    *   **Altın / Kehribar (Gold):** `#d4af37` ve `#c5a028` (Butonlar, vurgular, kenarlıklar ve özel bildirimler için)
    *   **Zeytin Yeşili (Olive Wreath):** `#556b2f` ve `#3b4e18` (Doğallık ve ferahlık katan ikincil renkler)
    *   **Lüks Krem / Kırık Beyaz:** `#FAF8F5` ve `#F5F2EB` (Arka planlar, kart zeminleri ve yumuşak geçişler)
*   **Arayüz Tercihleri:**
    *   Tasarımın her zaman **ultra-premium**, organik, temizlik ve ferahlık hissi veren lüks bir yapıda olması şarttır.
    *   **Cam Morfolojisi (Glassmorphism):** Buzlu cam görünümlü paneller, yumuşak gölgeler (`box-shadow`), ince altın kenarlıklar (`border: 1px solid rgba(212, 175, 55, 0.2)`).
    *   **Mikro-animasyonlar:** CTA butonlarında nefes alma/ışık süzülmesi efekti, hover durumlarında yumuşak büyüme ve kaymalar.

---

## 📈 Entegrasyon ve Fonksiyonellik İlkeleri

*   **YouTube Video Entegrasyonu:** Ürün tanıtım videoları için harici R2 yükü yerine YouTube embed oynatıcısı kullanılacaktır (reklam yayılımı ve organik trafik için).
*   **Sürtünmesiz Hızlı İletişim / Sipariş:** 
    *   Sitede sepet veya telefon numarası tabanlı form/sipariş olmayacaktır. 
    *   Kullanıcılar doğrudan ürünü satın almak, bilgi almak veya sipariş oluşturmak için resmi Instagram hesabına (**`@es_yasam`**) veya doğrudan Instagram DM sayfasına yönlendirilecektir (`https://instagram.com/es_yasam`). Butonlar bu Instagram bağlantısına premium bir şekilde entegre edilecektir.
*   **Performans ve SEO:** Astro'nun statik HTML çıktıları korunacak, LCP (Largest Contentful Paint) optimizasyonu için resimler WebP formatında optimize edilecektir.

---

## 🚀 Dağıtım ve Otomasyon Kuralları (Deployment & Automation)

*   **Otomatik Push Onayı:** Yerel ortamda başarıyla derlenen (`npm run build` hatasız tamamlanan) tüm web sitesi değişiklikleri, kullanıcıdan ekstra bir onay beklenmeksizin doğrudan GitHub `main` dalına push edilmelidir. Bu sayede canlı ortamdaki (Cloudflare Pages) güncellemeler kullanıcı tarafından online olarak hızlıca kontrol edilebilir.

