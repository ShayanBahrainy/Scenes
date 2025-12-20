import subprocess
import os
import threading

cmd_format = """
ffmpeg -i "{video_path}" -r 30 -c:v libvpx-vp9 -speed 4 -an -vf "scale=640:-2" -b:v 750k "{video_folder}/video_1.webm" -c:v libvpx-vp9 -speed 4 -an -vf "scale=640:-2" -b:v 1000k "{video_folder}/video_2.webm" -c:v libvpx-vp9 -speed 4 -an -vf "scale=1280:-2" -b:v 3000k "{video_folder}/video_3.webm" -c:v libvpx-vp9 -speed 4 -an -vf "scale=3840:-2" -b:v 12000k "{video_folder}/video_4.webm"

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
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True) as process:
            for line in process.stdout:
                print(line, end='', flush=True)
            process.stdout.close()
            process.wait()
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
            continue
        video_processor = VideoProcessor(video_folder=video_folder, video_path=complete_vid_path)
        video_processor.run()
