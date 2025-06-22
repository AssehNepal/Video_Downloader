from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
import os, re, tempfile

app = Flask(__name__)

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

        # Best quality progressive stream
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        filename = sanitize(yt.title) + ".mp4"

        # Create a temp file in system temp directory
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        # Download to file
        stream.download(output_path=temp_dir, filename=filename)

        # Send file to user
        response = send_file(file_path, as_attachment=True, download_name=filename)

        # Delete file after sending
        @response.call_on_close
        def remove_temp_file():
            if os.path.exists(file_path):
                os.remove(file_path)

        return response

    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
