import subprocess
import os
import threading

cmd_format = """
ffmpeg -i "{video_path}" -vn -acodec libvorbis -ab 128k -dash 1 "{video_folder}/audio.webm"

ffmpeg -i "{video_path}" -c:v libvpx-vp9 -keyint_min 150 \
-g 150 -tile-columns 4 -frame-parallel 1 -f webm -dash 1 \
-an -vf scale=160:90 -b:v 250k -dash 1 "{video_folder}/video_0.webm" \
-an -vf scale=320:180 -b:v 500k -dash 1 "{video_folder}/video_1.webm" \
-an -vf scale=640:360 -b:v 750k -dash 1 "{video_folder}/video_2.webm" \
-an -vf scale=640:360 -b:v 1000k -dash 1 "{video_folder}/video_3.webm" \
-an -vf scale=1280:720 -b:v 3000k -dash 1 "{video_folder}/video_4.webm"

ffmpeg \
  -f webm_dash_manifest -i "{video_folder}/video_0.webm" \
  -f webm_dash_manifest -i "{video_folder}/video_1.webm" \
  -f webm_dash_manifest -i "{video_folder}/video_2.webm" \
  -f webm_dash_manifest -i "{video_folder}/video_3.webm" \
  -f webm_dash_manifest -i "{video_folder}/video_4.webm" \
  -f webm_dash_manifest -i "{video_folder}/audio.webm" \
  -c copy \
  -map 0 -map 1 -map 2 -map 3 -map 4 -map 5\
  -f webm_dash_manifest \
  -adaptation_sets "id=0,streams=0,1,2,3,4 id=1,streams=5" \
  "{video_folder}/video_manifest.mpd"

"""


path = "/home/shayanbahrainy/Videos/Nature vids/final"
dest_path = "videos"

class Video:
    def __init__(self, src: str, video_name: str):
        self.src = src
        self.video_name = video_name

class VideoProcessor(threading.Thread):
    #Template for Master playlist of any draft
    DRAFT_MASTER_TEMPLATE = "\
    #EXTM3U\n\
    #EXT-X-STREAM-INF:BANDWIDTH=3572754,RESOLUTION=640x360\n\
    {video_folder_path}/360/360_video.m3u8\n\
    #EXT-X-STREAM-INF:BANDWIDTH=10289142,RESOLUTION=1280x720\n\
    {video_folder_path}/720/720_video.m3u8\n\
    #EXT-X-STREAM-INF:BANDWIDTH=18845789,RESOLUTION=1920x1080\n\
    {video_folder_path}/1080/1080_video.m3u8\n\
    "
    def __init__(self, video_path: os.PathLike, video_folder: os.PathLike, move_path: os.PathLike=None):
        """Processes videos into HLS Streams, if move_path is given, video_folder is moved there after the operation"""
        super().__init__()
        try:
            os.mkdir(video_folder)
        except:
            pass
        self.video_path = video_path
        self.video_folder = video_folder
        self.move_path = move_path

    def run(self):
        cmd = cmd_format.format(video_folder=self.video_folder, video_path=self.video_path)
        VideoProcessor.__call_ffmpeg__(cmd)
        if self.move_path:
            os.rename(self.video_folder, self.move_path)

    @staticmethod
    def __call_ffmpeg__(cmd):
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            print(process.communicate())
        return True



if __name__ == "__main__":
    for vid in os.listdir(path):
        complete_vid_path = path + "/" + vid
        video_name = vid.split(".")[0]
        print("Delete " + video_name + " folder before resuming program, if closed here. ")
        video_folder = dest_path + "/" + video_name
        try:
            os.mkdir(video_folder)
        except:
            print("Video already processed")
        video_processor = VideoProcessor(video_folder=video_folder, video_path=complete_vid_path)
        video_processor.run()