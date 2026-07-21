from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Store playlist in memory
playlist = []

def load_existing_files():
    """Load existing files from uploads folder into playlist on startup"""
    global playlist
    playlist = []  # Clear current playlist
    
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            if allowed_file(filename):
                song_info = {
                    'id': len(playlist),
                    'filename': filename,
                    'title': filename.rsplit('.', 1)[0],
                    'path': f'/static/uploads/{filename}'
                }
                playlist.append(song_info)
        print(f"Loaded {len(playlist)} existing songs")

@app.route('/')
def index():
    return render_template('index.html', playlist=playlist)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            return jsonify({'error': 'File already exists'})
        
        file.save(filepath)
        
        # Add to playlist
        song_info = {
            'id': len(playlist),
            'filename': filename,
            'title': filename.rsplit('.', 1)[0],
            'path': f'/static/uploads/{filename}'
        }
        playlist.append(song_info)
        
        return jsonify({'success': True, 'song': song_info})
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/playlist')
def get_playlist():
    return jsonify(playlist)

@app.route('/delete/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Optional: Add ability to delete songs"""
    global playlist
    if 0 <= song_id < len(playlist):
        song = playlist[song_id]
        # Delete file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], song['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        # Remove from playlist
        playlist.pop(song_id)
        # Reindex remaining songs
        for i, song in enumerate(playlist):
            song['id'] = i
        return jsonify({'success': True})
    return jsonify({'error': 'Song not found'})

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Load existing files on startup
    load_existing_files()
    
    app.run(debug=True)