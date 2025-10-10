import os

compiled_path = "/home/shayanbahrainy/Videos/Nature vids/complete"

compiled = os.listdir(compiled_path)


dest_path = "/home/shayanbahrainy/Videos/Nature vids/final/"

all_path = "/home/shayanbahrainy/Videos/iPhone/"

all = os.listdir(all_path)

accepted_ids = set([file.split(".")[0].strip("IMG_") for file in compiled])

for video in all:
    if video.split(".")[0].strip("_IMG") in accepted_ids:
        os.rename(all_path + video, dest_path + video)