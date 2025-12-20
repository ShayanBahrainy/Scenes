from flask import *
from werkzeug.security import safe_join
from streamer import Streamer
import os

app = Flask(__name__)
app.config['RELOAD_TEMPLATES'] = True
VIDEO_FOLDER="videos/"
streamer = Streamer(VIDEO_FOLDER, 10)

@app.route("/")
def index():
    return render_template("play_test.html")

@app.route("/video_<quality>_seg<seg_num>.webm")
def return_video_file(quality, seg_num):
    folder = streamer.get_segment_folder(seg_num)

    path = safe_join(VIDEO_FOLDER, safe_join(folder, "video_" + quality + ".webm"))
    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range")
    if range_header == None:
        return send_file(path, mimetype="video/webm")

    bytes = range_header.strip().split("=")[1]
    start, end = bytes.split("-")

    try:
        start = int(start)
        end = int(end)
    except:
        abort(400, "Invalid range header")


    if start >= file_size or end >= file_size or start > end:
        abort(416, "Requested Range Not Satisfiable")

    length = end - start + 1

    with open(path, "rb") as f:
        f.seek(start)
        data = f.read()


    return Response(
            data,
            status=206,
            mimetype="video/webm",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length)
            }
        )

@app.route("/audio_seg<seg_num>.webm")
def return_audio_file(seg_num):
    folder = streamer.get_segment_folder(seg_num)

    path = safe_join(VIDEO_FOLDER, safe_join(folder, "audio.webm"))
    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range")
    if range_header == None:
        return send_file(path, mimetype="audio/webm")


    bytes = range_header.strip().split("=")[1]
    start, end = bytes.split("-")

    try:
        start = int(start)
        end = int(end)
    except:
        abort(400, "Invalid range header")


    if start >= file_size or end >= file_size or start > end:
        abort(416, "Requested Range Not Satisfiable")

    length = end - start + 1

    with open(path, "rb") as f:
        f.seek(start)
        data = f.read()


    return Response(
            data,
            status=206,
            mimetype="audio/webm",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length)
            }
        )

app.run(debug=True)