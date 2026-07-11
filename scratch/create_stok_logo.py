#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageFilter

def create_cream_background():
    """Es Yaşam için premium açık krem tonlarında, derinlik hissi veren dikey gradyan."""
    small_bg = Image.new("RGBA", (1, 1200))
    for y in range(1200):
        ratio = y / 1200.0
        r = int(252 * (1.0 - ratio) + 244 * ratio)
        g = int(250 * (1.0 - ratio) + 238 * ratio)
        b = int(244 * (1.0 - ratio) + 224 * ratio)
        small_bg.putpixel((0, y), (r, g, b, 255))
    return small_bg.resize((1200, 1200), Image.Resampling.BILINEAR)

def main():
    print("Generating premium stok_logo.webp...")
    
    # 1. Create the studio background
    bg = create_cream_background()
    
    # 2. Open logo.jpg if it exists
    logo_path = "public/images/logo.jpg"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo nicely (e.g. 500x500 px)
        logo_size = 500
        logo_resized = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Center coordinates
        x = (1200 - logo_size) // 2
        y = (1200 - logo_size) // 2
        
        # Paste logo onto background
        bg.paste(logo_resized, (x, y), logo_resized)
        print("✓ Successfully integrated logo.jpg into stok_logo.webp")
    else:
        print("! logo.jpg not found, creating a clean studio placeholder without logo")
        
    # 3. Save as stok_logo.webp in public/images
    output_dir = "public/images"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "stok_logo.webp")
    
    bg.convert("RGB").save(output_path, "WEBP", quality=90)
    print(f"✓ Premium stok_logo.webp generated successfully at {output_path}")

if __name__ == "__main__":
    main()
