"""
Script para generar favicon de AWS
Requiere: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_aws_favicon():
    # Crear imagen 32x32 con fondo naranja AWS
    size = 32
    img = Image.new('RGB', (size, size), color='#FF9900')
    draw = ImageDraw.Draw(img)
    
    # Dibujar "AWS" simple
    try:
        # Usar fuente por defecto
        font = ImageFont.load_default()
    except:
        font = None
    
    # Texto blanco "AWS"
    text = "AWS"
    # Calcular posición centrada (aproximada)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 2
    
    draw.text((x, y), text, fill='#232F3E', font=font)
    
    # Guardar en diferentes formatos
    img.save('favicon.ico', format='ICO', sizes=[(32, 32)])
    img.save('favicon-32x32.png', format='PNG')
    
    # Crear apple-touch-icon 180x180
    img_large = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_large.save('apple-touch-icon.png', format='PNG')
    
    print("✅ Favicons creados exitosamente!")

if __name__ == '__main__':
    create_aws_favicon()
