from PIL import Image
import os

# Definimos los tamaños por dispositivo
SIZES = {
    'desktop': (1920, 1080),
    'tablet': (1200, 800),
    'mobile': (750, 1334),
}

input_folder = 'imagenes_originales'
output_folder = 'imagenes_optimizadas'
html_output_path = os.path.join(output_folder, 'srcset.html')

os.makedirs(output_folder, exist_ok=True)

# Recorte centrado
def crop_center(image, target_width, target_height):
    width, height = image.size
    left = (width - target_width) / 2
    top = (height - target_height) / 2
    right = (width + target_width) / 2
    bottom = (height + target_height) / 2
    return image.crop((left, top, right, bottom))

# Lista para guardar bloques HTML
html_blocks = []

# Procesamiento de imágenes
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path).convert('RGB')

        print(f'\n📷 Procesando: {filename}')
        base_name = os.path.splitext(filename)[0]
        source_width, source_height = img.size

        image_versions = {}  # Guarda rutas para HTML

        for device, (target_w, target_h) in SIZES.items():
            img_resized = img.copy()
            output_path = os.path.join(output_folder, device)
            os.makedirs(output_path, exist_ok=True)

            # Verifica tamaño mínimo
            if source_width < target_w or source_height < target_h:
                print(f"⚠️ {device.upper()}: Imagen muy pequeña para recortar a {target_w}x{target_h}")
                continue

            # Ajuste de proporción
            img_ratio = img.width / img.height
            target_ratio = target_w / target_h

            if img_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                img_resized = crop_center(img, new_width, img.height)
            else:
                new_height = int(img.width / target_ratio)
                img_resized = crop_center(img, img.width, new_height)

            # Redimensionar
            img_resized = img_resized.resize((target_w, target_h), Image.LANCZOS)

            # Usar el mismo nombre con .webp
            new_filename = f'{base_name}.webp'
            save_path = os.path.join(output_path, new_filename)

            # Guardar imagen WebP
            img_resized.save(save_path, 'WEBP', quality=85)
            print(f'✅ {device} guardado como {new_filename}')

            # Ruta relativa para HTML
            relative_path = os.path.relpath(save_path, output_folder)
            image_versions[device] = relative_path.replace('\\', '/')

        # Crear bloque HTML
        if image_versions:
            html = f"""
<picture>
  {f'<source srcset="{'/media/' + image_versions.get("desktop")}" media="(min-width: 1200px)">' if "desktop" in image_versions else ''}
  {f'<source srcset="{'/media/' + image_versions.get("tablet")}" media="(min-width: 768px)">' if "tablet" in image_versions else ''}
  <img src="{'/media/' + image_versions.get("mobile", next(iter(image_versions.values())))}" alt="{base_name}">
</picture>
"""
            html_blocks.append(html)

# Guardar archivo HTML
with open(html_output_path, 'w', encoding='utf-8') as f:
    f.write("<!DOCTYPE html>\n<html>\n<body>\n")
    f.write("\n".join(html_blocks))
    f.write("\n</body>\n</html>")

print("\n📝 HTML generado en:", html_output_path)
