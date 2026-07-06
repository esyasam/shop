#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ES YAŞAM - Profesyonel Ürün Fotoğrafı Stüdyolaştırma Otomasyonu
Bu script, bir klasördeki tüm JPG/JPEG/PNG ürün resimlerini alır:
1. Arka planlarını yapay zeka (rembg) ile temizler.
2. Ürün boyutlarını stüdyo şablonuna göre orantılı ölçekler.
3. Altına yumuşak temas gölgesi (contact shadow) ekler.
4. Altındaki cam zemine gerçekçi sönümlenen yansıma (reflection) ekler.
5. 1200x1200px WebP formatında ES YAŞAM premium krem stüdyo şablonuna monte eder.
6. Sağ alt köşeye zarif yarı şeffaf "Es Yaşam" filigranı ekler.
"""

import os
import sys
import argparse

# Bağımlılık kontrolü ve otomatik bilgilendirme
try:
    from PIL import Image, ImageFilter, ImageDraw, ImageChops, ImageEnhance, ImageFont
except ImportError:
    print("\n[HATA] 'Pillow' kütüphanesi kurulu değil.")
    print("Yüklemek için: pip install Pillow")
    sys.exit(1)

try:
    from rembg import remove
except ImportError:
    print("\n[UYARI] 'rembg' (Arka Plan Silme) kütüphanesi kurulu değil.")
    print("Bu kütüphane ilk çalışmada yapay zeka modelini otomatik indirir ve arka planları siler.")
    print("Yüklemek için: pip install rembg")
    print("Eğer şimdi yüklemek istemiyorsanız, sadece boyutlandırma ve yansıma işlemleri yapılacaktır.")

# --- YAPILANDIRMA VE KALİBRASYON AYARLARI ---
PRODUCT_MAX_HEIGHT = 660  # Ürünün şablondaki maksimum dikey yüksekliği (px) (%10 büyütüldü, eski değer: 600)
PRODUCT_MAX_WIDTH = 800   # Ürünün şablondaki maksimum yatay genişliği (px) (%10 büyütüldü, eski değer: 725)
REFLECTION_OPACITY = 0.28  # Cam zemindeki yansımanın başlangıç şeffaflığı (0.0 - 1.0)
REFLECTION_BLUR = 5        # Yansımanın fluluk derecesi (Blur yarıçapı, yumuşak flu yansıma için)
SHADOW_OPACITY = 0.05      # Ürün altındaki gölgenin şeffaflığı (0.0 - 1.0) (Çok çok az gölge istendiği için eski 0.35 değeri düşürüldü)
SHADOW_BLUR = 12           # Gölgelerin yumuşaklık derecesi (Blur yarıçapı)
BACKGROUND_BLUR = 0        # Arka planın fluluk derecesi (Bokeh efekti, oluşturulan gradient için 0 kalsın)
BACKGROUND_SATURATION = 1.0  # Arka plan doygunluğu (Yaratılan gradyan için 1.0)
BACKGROUND_BRIGHTNESS = 1.0  # Arka plan parlaklığı (Yaratılan gradyan için 1.0)

def create_gradient_mask(width, height, start_opacity):
    """Yansımanın aşağı doğru pürüzsüzce sönümlenmesi için linear gradient maske üretir."""
    gradient = Image.new('L', (1, height))
    for y in range(height):
        # Üstte (temas noktası) en görünür, alta doğru tamamen şeffaflaşan gradient
        opacity = int(255 * start_opacity * (1.0 - (y / height)))
        gradient.putpixel((0, y), opacity)
    return gradient.resize((width, height), Image.Resampling.BILINEAR)

def create_contact_shadow(width, blur_radius, opacity):
    """Ürünün taban genişliğine göre eliptik ve yumuşak bir temas gölgesi üretir."""
    shadow_height = int(width * 0.12)  # İnce dikey elips
    if shadow_height < 6:
        shadow_height = 6
        
    shadow_canvas = Image.new('RGBA', (width + blur_radius * 3, shadow_height + blur_radius * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow_canvas)
    
    # Elips koordinatları
    left = blur_radius * 1.5
    top = blur_radius * 1.5
    right = left + width
    bottom = top + shadow_height
    
    draw.ellipse([left, top, right, bottom], fill=(0, 0, 0, int(255 * opacity)))
    return shadow_canvas.filter(ImageFilter.GaussianBlur(blur_radius))

def create_cream_background():
    """Es Yaşam için premium açık krem tonlarında, derinlik hissi veren hafif dikey gradyan arka plan oluşturur."""
    # Üst: #FCFAF4 (Sıcak beyaz/çok açık krem), Alt: #F4EEE0 (Yumuşak sıcak krem/bej)
    small_bg = Image.new("RGBA", (1, 1200))
    for y in range(1200):
        ratio = y / 1200.0
        r = int(252 * (1.0 - ratio) + 244 * ratio)
        g = int(250 * (1.0 - ratio) + 238 * ratio)
        b = int(244 * (1.0 - ratio) + 224 * ratio)
        small_bg.putpixel((0, y), (r, g, b, 255))
    return small_bg.resize((1200, 1200), Image.Resampling.BILINEAR)

def add_watermark(image, text="Es Yaşam"):
    """Görsele zarif, yarı şeffaf ve warm-grey tonlarında 'Es Yaşam' filigranı ekler."""
    txt_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Premium font yollarını dene
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "Arial.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 30)
                break
            except Exception:
                pass
                
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
            
    # Konum hesaplama (Sağ alt köşe, 45px pay ile)
    width, height = image.size
    margin = 45
    
    if font:
        try:
            # Pillow 10+ için modern text bbox tespiti
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            # Eski Pillow sürümleri için fallback
            text_w, text_h = draw.textsize(text, font=font)
            
        x = width - text_w - margin
        y = height - text_h - margin
        
        # Açık krem arka plana uyumlu soft toprak tonlu yarı şeffaf koyu gri
        color = (90, 85, 80, 85)
        
        # Metni çiz
        draw.text((x, y), text, fill=color, font=font)
        
    return Image.alpha_composite(image, txt_layer)

def process_single_image(img_path, output_path, template_img):
    """Tek bir ürün görselini işler, stüdyoya monte eder ve kaydeder."""
    print(f"\n⏳ İşleniyor: {os.path.basename(img_path)}")
    
    try:
        # 1. Görseli Aç
        raw_img = Image.open(img_path)
        
        # 2. Arka Planı Temizle (rembg kurulu ise)
        if 'remove' in globals():
            print("   ↳ Yapay zeka ile arka plan temizleniyor...")
            no_bg_img = remove(raw_img)
        else:
            print("   ↳ [PAS GEÇİLDİ] rembg kurulu olmadığı için arka plan silinmedi (PNG ise şeffaflık korunur).")
            no_bg_img = raw_img.convert("RGBA")
            
        # 3. Görünmez Gürültüleri Eşikle ve Boş Kenar Boşluklarını Kırp (Autocrop)
        if no_bg_img.mode == 'RGBA':
            r, g, b, a = no_bg_img.split()
            a = a.point(lambda p: 0 if p < 15 else p)
            no_bg_img = Image.merge('RGBA', (r, g, b, a))

        bbox = no_bg_img.getbbox()
        if bbox:
            cropped_img = no_bg_img.crop(bbox)
        else:
            cropped_img = no_bg_img

        # 4. Ürünü Orantılı Ölçeklendir
        orig_w, orig_h = cropped_img.size
        scale = min(PRODUCT_MAX_WIDTH / orig_w, PRODUCT_MAX_HEIGHT / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        product_resized = cropped_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Sahnemizi Kopyala (Şablon üzerinde çalışacağız)
        scene = template_img.copy()
        
        # Ürün koordinatlarını hesapla (Dikey ve yatayda tam ortalanacak şekilde)
        product_x = (1200 - new_w) // 2
        product_y = (1200 - new_h) // 2
        
        # Dinamik dikey hizalama çizgisi (yansıma ve gölgenin yaslanacağı taban çizgisi)
        dynamic_table_line_y = product_y + new_h
        
        # 5. GERÇEKÇİ CAM YANSIMASI (Reflection) EKLE
        print("   ↳ Cam yansıması hesaplanıyor...")
        flipped_product = product_resized.transpose(Image.FLIP_TOP_BOTTOM)
        
        # Yansımayı daha doğal ve flu yapmak için Gaussian Blur filtresi uyguluyoruz
        if 'REFLECTION_BLUR' in globals() and REFLECTION_BLUR > 0:
            flipped_product = flipped_product.filter(ImageFilter.GaussianBlur(REFLECTION_BLUR))
            
        mask = create_gradient_mask(new_w, new_h, REFLECTION_OPACITY)
        
        if flipped_product.mode == 'RGBA':
            flipped_alpha = flipped_product.split()[3]
            combined_mask = ImageChops.multiply(flipped_alpha, mask)
        else:
            combined_mask = mask
            
        # Yansımayı sahneye dinamik taban çizgisinden aşağıya doğru monte et
        scene.paste(flipped_product, (product_x, dynamic_table_line_y), combined_mask)
        
        # 6. YUMUŞAK TEMAS GÖLGESİ (Contact Shadow) EKLE
        print("   ↳ Yumuşak temas gölgesi çiziliyor...")
        shadow_blur = SHADOW_BLUR
        shadow_img = create_contact_shadow(new_w, shadow_blur, SHADOW_OPACITY)
        shadow_x = product_x - int(shadow_blur * 1.5)
        shadow_y = dynamic_table_line_y - int(shadow_img.height / 2)
        scene.paste(shadow_img, (shadow_x, shadow_y), shadow_img)
        
        # 7. ASIL ÜRÜNÜ MONTE ET
        print("   ↳ Ürün sahneye yerleştiriliyor...")
        scene.paste(product_resized, (product_x, product_y), product_resized)
        
        # 7.5 ZARİF ES YAŞAM FİLİGRANI EKLE
        print("   ↳ 'Es Yaşam' filigranı ekleniyor...")
        scene = add_watermark(scene, "Es Yaşam")
        
        # 8. WebP OLARAK KAYDET
        scene_rgb = scene.convert("RGB")
        scene_rgb.save(output_path, "WEBP", quality=90)
        print(f"   ✓ Tamamlandı! Kaydedilen Dosya: {output_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ HATA oluştu: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ES YAŞAM Ürün Fotoğrafı Stüdyolaştırma Otomasyonu")
    parser.add_argument("--input", default="product_images", help="Giriş görsellerinin bulunduğu klasör")
    parser.add_argument("--output", default="processed_products", help="İşlenmiş görsellerin kaydedileceği klasör")
    args = parser.parse_args()
    
    # Klasörleri kontrol et ve oluştur
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"\n[BİLGİ] '{args.input}' klasörü oluşturuldu. Lütfen ham ürün resimlerinizi bu klasöre atın.")
        print("Ardından bu scripti tekrar çalıştırın.")
        sys.exit(0)
        
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    # Açık krem premium arka planı bellekte oluştur
    template_img = create_cream_background()
        
    # Desteklenen uzantılar
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    image_files = [f for os_dir, _, files in os.walk(args.input) for f in files if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print(f"\n[BİLGİ] '{args.input}' klasöründe işlenecek görsel bulunamadı.")
        print("Uzantısı .jpg, .jpeg, .png veya .webp olan ham ürün görsellerinizi bu klasöre yükleyin.")
        sys.exit(0)
        
    print(f"\n========================================================")
    print(f"🌾 ES YAŞAM - TOPLU ÜRÜN STÜDYO DÖNÜŞTÜRÜCÜ BAŞLATILDI 🌾")
    print(f"========================================================")
    print(f"📂 Ham Ürün Klasörü : {args.input}")
    print(f"📂 Çıktı Klasörü    : {args.output}")
    print(f"🏷️ Seçilen Marka     : Es Yaşam (Açık Krem Minimalist Stüdyo)")
    print(f"🖼️ Toplam Görsel    : {len(image_files)} adet")
    print(f"--------------------------------------------------------")
    
    success_count = 0
    for filename in image_files:
        input_file_path = os.path.join(args.input, filename)
        basename = os.path.splitext(filename)[0]
        output_file_path = os.path.join(args.output, f"{basename}.webp")
        
        if process_single_image(input_file_path, output_file_path, template_img):
            success_count += 1
            
    print(f"\n========================================================")
    print(f"🎉 İŞLEM TAMAMLANDI! 🎉")
    print(f"========================================================")
    print(f"✅ Başarıyla İşlenen : {success_count} / {len(image_files)}")
    print(f"📁 Kaydedilen Klasör : {args.output}")
    print(f"========================================================")

if __name__ == "__main__":
    main()
