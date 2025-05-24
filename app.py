from flask import Flask, request, render_template, send_from_directory
import os
import hashlib
from PIL import Image, ImageOps
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_photos'
THUMBNAIL_FOLDER = 'thumbnails'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
PHOTOS_PER_PAGE = 30
THUMBNAIL_SIZE = (200, 200) # Define the desired thumbnail size (width, height)

def crop_and_resize_to_square(img, size):
    """
    Crops the image to a square from its center and then resizes it.
    """
    width, height = img.size
    
    if width > height:
        # Crop to a square from the center (horizontally)
        left = (width - height) / 2
        top = 0
        right = (width + height) / 2
        bottom = height
    else:
        # Crop to a square from the center (vertically)
        left = 0
        top = (height - width) / 2
        right = width
        bottom = (height + width) / 2
    
    img = img.crop((left, top, right, bottom))
    img = img.resize(size, Image.LANCZOS) # Use LANCZOS for high-quality downsampling

    if img.mode == 'RGBA':
        # Create a new opaque image with a black background
        background = Image.new('RGB', img.size, (0, 0, 0))
        # Composite the RGBA image onto the background
        background.paste(img, (0, 0), img) # The third argument (mask) is important for RGBA
        img = background

    return img

@app.route('/', methods=['GET', 'POST'])
def upload_photos():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('photos')
        for file in uploaded_files:
            if file and file.filename != '':
                file_content = file.read()
                file_hash = hashlib.sha256(file_content).hexdigest()
                file_extension = os.path.splitext(file.filename)[1].lower()
                filename = f'{file_hash}{file_extension}' # This is the original uploaded filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_content)

                # All thumbnails will be saved as .jpg for consistency, using the hash
                thumbnail_filename_for_display = f'{file_hash}.jpg'
                thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_filename_for_display)

                if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    try:
                        img = Image.open(filepath)
                        img = ImageOps.exif_transpose(img) # Corrects orientation based on EXIF data
                        img = crop_and_resize_to_square(img, THUMBNAIL_SIZE)
                        img.save(thumbnail_path)
                    except Exception as e:
                        print(f'Error generating image thumbnail: {e}')
                elif file_extension in ['.mp4', '.webm', '.ogg', '.mov']:
                    temp_video_thumbnail_path = os.path.join(THUMBNAIL_FOLDER, f'{file_hash}_temp.jpg')
                    try:
                        subprocess.run([
                            'ffmpeg',
                            '-y',  # Overwrite output files without asking
                            '-i', filepath, 
                            '-ss', '00:00:01.000', # Seek to 1 second
                            '-vframes', '1', 
                            '-update', '1', # Critical for single frame output
                            temp_video_thumbnail_path
                        ], check=True)

                        if os.path.exists(temp_video_thumbnail_path):
                            img = Image.open(temp_video_thumbnail_path)
                            img = crop_and_resize_to_square(img, THUMBNAIL_SIZE)
                            img.save(thumbnail_path)
                            os.remove(temp_video_thumbnail_path) # Clean up the temporary file
                        else:
                            print(f"FFmpeg did not create temporary thumbnail for {filepath}")

                    except subprocess.CalledProcessError as e:
                        if e.stderr:
                             print(f'Error generating temporary video thumbnail with FFmpeg: {e.stderr}')
                        else:
                             print(f'Error generating temporary video thumbnail with FFmpeg (no stderr captured, check console for FFmpeg output): {e}')
                    except Exception as e:
                        print(f'Error processing video thumbnail with PIL: {e}')

    page = int(request.args.get('page', 1))
    
    # Get all original uploaded files
    all_uploaded_files = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    
    # Map original filenames to their corresponding .jpg thumbnail filenames
    # And create a list of dictionaries to hold both original file info and thumbnail file info
    all_gallery_items = []
    for original_file_with_ext in all_uploaded_files:
        file_hash_part, original_ext = os.path.splitext(original_file_with_ext)
        
        gallery_item = {
            'original_filename': original_file_with_ext,
            'thumbnail_filename': f'{file_hash_part}.jpg', # This is what we pass to thumbnail_file
            'is_video': original_ext.lower() in ['.mp4', '.webm', '.ogg', '.mov']
        }
        all_gallery_items.append(gallery_item)

    start = (page - 1) * PHOTOS_PER_PAGE
    end = start + PHOTOS_PER_PAGE
    paginated_gallery_items = all_gallery_items[start:end]


    prev_page = page - 1 if start > 0 else None
    next_page = page + 1 if end < len(all_gallery_items) else None # Use all_gallery_items for total count

    return render_template('gallery.html', gallery_items=paginated_gallery_items, prev_page=prev_page, next_page=next_page)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

@app.route('/thumbnails/<path:filename>')
def thumbnail_file(filename):
    return send_from_directory(THUMBNAIL_FOLDER, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

