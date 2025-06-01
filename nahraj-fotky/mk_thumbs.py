from PIL import Image
import pillow_heif
import os

pillow_heif.register_heif_opener()

src_dir = "uploaded_photos"
dst_dir = "thumbnails"

os.makedirs(dst_dir, exist_ok=True)

supported_exts = [".heic", ".jpg", ".jpeg", ".png", ".webp"]

for fname in os.listdir(src_dir):
    ext = os.path.splitext(fname)[1].lower()
    if ext not in supported_exts:
        continue

    dst_path = os.path.join(dst_dir, os.path.splitext(fname)[0] + ".jpg")
    if os.path.exists(dst_path):
        print(f"Thumbnail už existuje, přeskočeno: {dst_path}")
        continue

    src_path = os.path.join(src_dir, fname)
    try:
        img = Image.open(src_path)
        img = img.convert("RGB")

        width, height = img.size
        min_side = min(width, height)
        left = (width - min_side) // 2
        top = (height - min_side) // 2
        img = img.crop((left, top, left + min_side, top + min_side))
        img = img.resize((200, 200), Image.ANTIALIAS)

        img.save(dst_path, "JPEG")
        print(f"Thumbnail uložen: {dst_path}")
    except Exception as e:
        print(f"Chyba u {fname}: {e}")

