from flask import Flask, request, render_template, send_from_directory
import os
import hashlib
from PIL import Image
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_photos'
THUMBNAIL_FOLDER = 'thumbnails'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
PHOTOS_PER_PAGE = 50

@app.route('/', methods=['GET', 'POST'])
def upload_photos():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('photos')
        for file in uploaded_files:
            if file and file.filename != '':
                file_content = file.read()
                file_hash = hashlib.sha256(file_content).hexdigest()
                file_extension = os.path.splitext(file.filename)[1].lower()
                filename = f'{file_hash}{file_extension}'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_content)

                thumbnail_path = os.path.join(THUMBNAIL_FOLDER, filename + '.jpg')

                if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    try:
                        img = Image.open(filepath)
                        img.thumbnail((200, 200))
                        img.save(thumbnail_path)
                    except Exception as e:
                        print(f'Error generating image thumbnail: {e}')
                elif file_extension in ['.mp4', '.webm', '.ogg', '.mov']:
                    try:
                        subprocess.run(['ffmpeg', '-y', '-i', filepath, '-ss', '00:00:01.000', '-vframes', '1', '-update', '1', thumbnail_path], check=True)
                    except Exception as e:
                        print(f'Error generating video thumbnail: {e}')

    page = int(request.args.get('page', 1))
    photos = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    start = (page - 1) * PHOTOS_PER_PAGE
    end = start + PHOTOS_PER_PAGE
    paginated_photos = photos[start:end]

    prev_page = page - 1 if start > 0 else None
    next_page = page + 1 if end < len(photos) else None

    return render_template('gallery.html', photos=paginated_photos, prev_page=prev_page, next_page=next_page)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

@app.route('/thumbnails/<path:filename>')
def thumbnail_file(filename):
    return send_from_directory(THUMBNAIL_FOLDER, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

