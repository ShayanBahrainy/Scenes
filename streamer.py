import os
import secrets
import utils
import threading
import random

class Streamer:
    def __init__(self: 'Streamer', video_folder: str, consistency_period: int):
        self.video_folder = video_folder
        self.consistency_period = consistency_period

    def get_segment_folder(self: 'Streamer', num: int) -> str:
        try:
            num = int(num)
        except ValueError:
            raise TypeError("Num must be an number.")

        seed = num + round(utils.get_time() / (self.consistency_period * 60)) * (self.consistency_period * 60)

        rng = random.Random(seed)

        possible_videos = os.listdir(self.video_folder)


        return rng.choice(possible_videos)

