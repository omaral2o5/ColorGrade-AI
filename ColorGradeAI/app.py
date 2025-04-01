from flask import Flask, request, send_file
from color_transfer import apply_color_transfer
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload Files</title>
    <h1>Upload Reference Image and Target Video</h1>
    <form method="post" enctype="multipart/form-data" action="/upload">
      <label>Reference Image:</label><br />
      <input type="file" name="reference"><br /><br />
      <label>Target Video:</label><br />
      <input type="file" name="video"><br /><br />
      <input type="submit" value="Upload">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    reference = request.files.get('reference')
    target = request.files.get('video')

    if not reference or not target:
        return 'Missing files', 400

    ref_path = os.path.join(UPLOAD_FOLDER, f'ref_{uuid.uuid4()}.jpg')
    video_path = os.path.join(UPLOAD_FOLDER, f'vid_{uuid.uuid4()}.mp4')
    output_path = os.path.join(OUTPUT_FOLDER, f'out_{uuid.uuid4()}.mp4')

    reference.save(ref_path)
    target.save(video_path)

    apply_color_transfer(ref_path, video_path, output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
