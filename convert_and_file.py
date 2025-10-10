import subprocess
import os

cmd_format = """
mkdir "{video_folder}/360"
mkdir "{video_folder}/720"
mkdir "{video_folder}/1080"
ffmpeg -i "{video_path}" -profile:v high10 -level 3.0 -vf "scale=640:-2"  -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/360/360_video.m3u8"
ffmpeg -i "{video_path}" -profile:v high10 -level 3.0 -vf "scale=1280:-2"  -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/720/720_video.m3u8"
ffmpeg -i "{video_path}" -profile:v high10 -level 3.0 -vf "scale=1920:-2"  -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{video_folder}/1080/1080_video.m3u8"
"""

path = "/home/shayanbahrainy/Videos/Nature vids/final"
dest_path = "/home/shayanbahrainy/Videos/Nature vids/converted"
def call_ffmpeg(cmd):
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        print(process.communicate())
    return True


for video in os.listdir(path):
    video_name = video.split(".")[0]
    print("Delete " + video_name + " folder before resuming program, if closed here. ")
    video_folder = dest_path + "/" + video_name
    try:
        os.mkdir(video_folder)
    except:
        continue
    cmd = cmd_format.format(video_folder=video_folder, video_path=path+"/"+video)
    call_ffmpeg(cmd)