function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select files to upload');
        return;
    }
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addToPlaylist(data.song);
            } else {
                alert('Upload failed: ' + data.error);
            }
        });
    }
}

function addToPlaylist(song) {
    const playlist = document.getElementById('playlistContainer');
    const li = document.createElement('li');
    li.textContent = song.title;
    li.onclick = () => playSong(song.path, song.title);
    playlist.appendChild(li);
}

function playSong(path, title) {
    const player = document.getElementById('audioPlayer');
    const currentSong = document.getElementById('currentSong');
    
    player.src = path;
    player.play();
    currentSong.textContent = `Now playing: ${title}`;
}

function deleteSong(songId) {
    if (confirm('Delete this song?')) {
        fetch(`/delete/${songId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Refresh page
            }
        });
    }
}