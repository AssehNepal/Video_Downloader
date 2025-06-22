from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
import os, re, tempfile, subprocess

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

        # Get best quality video-only and audio-only streams
        video_stream = yt.streams.filter(progressive=False, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()

        filename = sanitize(yt.title) + ".mp4"
        temp_dir = tempfile.gettempdir()

        video_path = os.path.join(temp_dir, "video.mp4")
        audio_path = os.path.join(temp_dir, "audio.mp4")
        final_path = os.path.join(temp_dir, filename)

        # Download both video and audio
        video_stream.download(output_path=temp_dir, filename="video.mp4")
        audio_stream.download(output_path=temp_dir, filename="audio.mp4")

        # Merge using system ffmpeg
        subprocess.run([
            "ffmpeg", "-y",  # overwrite if file exists
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",     # fast copy without re-encoding
            "-c:a", "aac",      # standard audio codec
            "-strict", "experimental",
            final_path
        ], check=True)

        # Serve the merged file
        response = send_file(final_path, as_attachment=True, download_name=filename)

        # Clean up all temp files after the file is sent
        @response.call_on_close
        def cleanup():
            for path in [video_path, audio_path, final_path]:
                if os.path.exists(path):
                    os.remove(path)

        return response

    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
