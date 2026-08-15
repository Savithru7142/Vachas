import base64
import os

from PIL import Image, ImageDraw


def create_logo_assets():
    src_path = 'static/img/logo/original_logo.jpg'
    img = Image.open(src_path).convert('RGBA')

    # Circle coordinates
    cx, cy = 164.5, 140.5
    r = 127.5

    # Crop square around circle center
    left = round(cx - r)
    top = round(cy - r)
    right = round(cx + r)
    bottom = round(cy + r)

    cropped = img.crop((left, top, right, bottom))

    # Resize to high resolution master (512x512)
    master_size = 512
    resized = cropped.resize((master_size, master_size), Image.Resampling.LANCZOS)

    # 4x supersampled smooth circular mask
    scale = 4
    mask = Image.new('L', (master_size * scale, master_size * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, master_size * scale - 1, master_size * scale - 1), fill=255)
    mask = mask.resize((master_size, master_size), Image.Resampling.LANCZOS)

    master = Image.new('RGBA', (master_size, master_size), (0, 0, 0, 0))
    master.paste(resized, (0, 0), mask=mask)

    # Save to static/img/logo and staticfiles/img/logo
    for folder in ['static/img/logo', 'staticfiles/img/logo']:
        os.makedirs(folder, exist_ok=True)
        master.save(os.path.join(folder, 'vachas-logo.png'), 'PNG')
        master.save(os.path.join(folder, 'logo.png'), 'PNG')
        master.save(os.path.join(folder, 'apple-touch-icon.png'), 'PNG')

        # Favicon 32x32 and 16x16
        fav = master.resize((32, 32), Image.Resampling.LANCZOS)
        fav.save(os.path.join(folder, 'favicon.png'), 'PNG')
        fav.save(os.path.join(folder, 'favicon-32x32.png'), 'PNG')
        fav16 = master.resize((16, 16), Image.Resampling.LANCZOS)
        fav16.save(os.path.join(folder, 'favicon-16x16.png'), 'PNG')
        master.save(os.path.join(folder, 'favicon.ico'), format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])

    # Also generate base64-embedded SVG fallback
    with open('static/img/logo/vachas-logo.png', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" role="img" aria-label="Vachas Logo">
  <image href="data:image/png;base64,{b64}" width="512" height="512" />
</svg>
'''
    for folder in ['static/img/logo', 'staticfiles/img/logo']:
        with open(os.path.join(folder, 'vachas-logo.svg'), 'w', encoding='utf-8') as f:
            f.write(svg_content)

    print("Generated all logo assets successfully!")


if __name__ == '__main__':
    create_logo_assets()
