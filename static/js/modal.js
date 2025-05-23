
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
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
    const modalVideo = document.getElementById('modal-video');
    modalVideo.pause();
    modalVideo.src = '';
}
// Update file input label with selected file names
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-upload');
    const uploadLabel = document.querySelector('label.upload-btn');
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length === 0) {
            uploadLabel.textContent = 'Nahraj fotky';
        } else if (fileInput.files.length === 1) {
            uploadLabel.textContent = fileInput.files[0].name;
        } else {
            uploadLabel.textContent = `${fileInput.files.length} souborů vybráno`;
        }
    });
});

