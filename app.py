from flask import Flask, request, render_template_string, send_from_directory
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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload Photos & Videos</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .container { max-width: 800px; margin: auto; padding: 10px; }
        form { margin-bottom: 20px; }
        .gallery { display: flex; flex-wrap: wrap; gap: 5px; }
        .gallery img { max-width: 100px; height: auto; cursor: pointer; }
        button { padding: 10px; font-size: 16px; }
        .pagination { margin-top: 20px; display: flex; justify-content: space-between; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.8); justify-content: center; align-items: center; }
        .modal img, .modal video { max-width: 90%; max-height: 90%; }
    </style>
    <script>
        function showMedia(src, isVideo) {
            const modal = document.getElementById('modal');
            const modalImg = document.getElementById('modal-img');
            const modalVideo = document.getElementById('modal-video');
            if (isVideo) {
                modalImg.style.display = 'none';
                modalVideo.style.display = 'block';
                modalVideo.src = src;
                modalVideo.play();
            } else {
                modalVideo.style.display = 'none';
                modalImg.style.display = 'block';
                modalImg.src = src;
            }
            modal.style.display = 'flex';
        }
        function hideMedia() {
            document.getElementById('modal').style.display = 'none';
            const modalVideo = document.getElementById('modal-video');
            modalVideo.pause();
            modalVideo.src = '';
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Upload Photos & Videos</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="photos" accept="image/*,video/*" multiple>
            <button type="submit">Upload</button>
        </form>
        <h2>Gallery</h2>
        <div class="gallery">
            {% for file in photos %}
                <img src="/thumbnails/{{ file }}.jpg" alt="Photo/Video" onclick="showMedia('/uploads/{{ file }}', '{{ file.lower().endswith(('.mp4', '.webm', '.ogg', '.mov')) }}' == 'True')">
            {% endfor %}
        </div>
        <div class="pagination">
            {% if prev_page is not none %}
                <a href="?page={{ prev_page }}"><button>Previous</button></a>
            {% endif %}
            {% if next_page is not none %}
                <a href="?page={{ next_page }}"><button>Next</button></a>
            {% endif %}
        </div>
    </div>
    <div id="modal" class="modal" onclick="hideMedia()">
        <img id="modal-img" src="" alt="Large View">
        <video id="modal-video" controls style="display:none;"></video>
    </div>
</body>
</html>
'''


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
                        subprocess.run(['ffmpeg', '-i', filepath, '-ss', '00:00:01.000', '-vframes', '1', '-update', '1', thumbnail_path], check=True)
                    except Exception as e:
                        print(f'Error generating video thumbnail: {e}')

    page = int(request.args.get('page', 1))
    photos = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    start = (page - 1) * PHOTOS_PER_PAGE
    end = start + PHOTOS_PER_PAGE
    paginated_photos = photos[start:end]

    prev_page = page - 1 if start > 0 else None
    next_page = page + 1 if end < len(photos) else None

    return render_template_string(HTML_TEMPLATE, photos=paginated_photos, prev_page=prev_page, next_page=next_page)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)


@app.route('/thumbnails/<path:filename>')
def thumbnail_file(filename):
    return send_from_directory(THUMBNAIL_FOLDER, filename, as_attachment=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

