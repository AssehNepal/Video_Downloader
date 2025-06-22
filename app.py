from flask import Flask, render_template, request, send_file
from pytubefix import YouTube  # instead of pytube

import os, re

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        filename = sanitize(yt.title) + ".mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        stream.download(output_path=DOWNLOAD_DIR, filename=filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return render_template('index.html', error=str(e))
    
# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)