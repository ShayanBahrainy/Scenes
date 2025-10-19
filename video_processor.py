import subprocess
import os
import threading

cmd_format = """
mkdir "{video_folder}/360"
mkdir "{video_folder}/720"
mkdir "{video_folder}/1080"
ffmpeg -i "{video_path}" -v error -profile:v high10 -level 3.0 -vf "scale=640:-2"  -start_number 0 -force_key_frames "expr:gte(t,n_forced*10)" -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/360/360_video.m3u8"
ffmpeg -i "{video_path}" -v error -profile:v high10 -level 3.0 -vf "scale=1280:-2"  -start_number 0 -force_key_frames "expr:gte(t,n_forced*10)" -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/720/720_video.m3u8"
ffmpeg -i "{video_path}" -v error -profile:v high10 -level 3.0 -vf "scale=1920:-2"  -start_number 0 -force_key_frames "expr:gte(t,n_forced*10)" -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/1080/1080_video.m3u8"
"""

path = "/home/shayanbahrainy/Videos/Nature vids/final"
dest_path = "/home/shayanbahrainy/Videos/Nature vids/converted"

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
    for video in os.listdir(path):
        video_name = video.split(".")[0]
        print("Delete " + video_name + " folder before resuming program, if closed here. ")
        video_folder = dest_path + "/" + video_name
        try:
            os.mkdir(video_folder)
        except:
            continue
        video_processor = VideoProcessor(video_folder=video_folder, video_path=path+"/"+video)