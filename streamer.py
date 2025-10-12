import os
import secrets
import time
import threading

MASTER_PLAYLIST = \
"""
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=3572754,RESOLUTION=640x360
360.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=10289142,RESOLUTION=1280x720
720.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=18845789,RESOLUTION=1920x1080
1080.m3u8
"""

MEDIA_COMPONENT = \
"""
#EXTINF:{length},
{path}
"""

MEDIA_PLAYLIST_TEMPLATE = \
"""
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION: {target_duration}
#EXT-X-MEDIA-SEQUENCE:0
{components}
"""

class Streamer(threading.Thread):
    THREE_SIXTY_P = "360"
    SEVEN_TWENTY_P = "720"
    TEN_EIGHTY_P = "1080"
    TARGET_LIST_LENGTH = 6
    TARGET_DURATION = 10

    @staticmethod
    def __add_basepath__(playlist: str, path: str):
        if path[-1] != "/" and path[-1] != "\\":
            path += "/"
        found = playlist.find("#EXTINF:", 0)
        while found != -1:
            found = playlist.find("\n", found)
            playlist = playlist[:found + 1] + path + playlist[found + 1:]
            found = playlist.find("#EXTINF:", found)
        return playlist

    @staticmethod
    def __replace_target_dur__(playlist: str, duration: float) -> str:
        duration = round(duration, 5)
        TARGET_DURATION_MARKER = "#EXT-X-TARGETDURATION:"
        target_dur_start = playlist.find(TARGET_DURATION_MARKER)
        target_dur_end = min(playlist.find(",", target_dur_start), playlist.find("\n", target_dur_start))
        playlist = playlist[:target_dur_start + len(TARGET_DURATION_MARKER)] + str(duration) + playlist[target_dur_end:]

        return playlist


    @staticmethod
    def __calculate_target_dur__(playlist: str) -> float:
        """DON'T USE, HERE FOR REFERENCE ONLY"""
        last_index = 0
        max_time = -1
        found_index = playlist.find("#EXTINF:", last_index)
        while found_index != -1:
            end_float = min(playlist.find("\n", found_index), playlist.find(",", found_index))
            found_index += len("#EXTINF:")
            max_time = max(float(playlist[found_index: end_float]), max_time)
            last_index = found_index
            found_index = playlist.find("#EXTINF:", last_index)
        return int(max_time)

    @staticmethod
    def __get_list_dur__(playlist: str) -> float:
        TARGET_DURATION_MARKER = "#EXT-X-TARGETDURATION:"
        target_dur_start = playlist.find(TARGET_DURATION_MARKER)
        target_dur_end = min(playlist.find(",", target_dur_start), playlist.find("\n", target_dur_start))
        return float(playlist[target_dur_start + len(TARGET_DURATION_MARKER):target_dur_end])

    @staticmethod
    def __append_lists__(playlist1: str, playlist2: str) -> str:
        "Appends playlist2 into playlist1"
        valid_lines = []

        second_lines = playlist2.split("\n")
        i = 0
        while i < len(second_lines):
            if "#EXT-X-DISCONTINUITY" in second_lines[i]:
                valid_lines.append(second_lines[i])
                valid_lines.append(second_lines[i + 1])
                valid_lines.append(second_lines[i + 2])
                i += 3
            if "#EXTINF:" in second_lines[i]:
                valid_lines.append(second_lines[i])
                valid_lines.append(second_lines[i + 1])
                i += 2
            i += 1

        last_file_line = 4 #First line after header
        first_lines = playlist1.split("\n")
        for i in range(len(first_lines)):
            if ".ts" in first_lines[i]:
                last_file_line = i

        i = last_file_line + 1
        first_lines.insert(i, "#EXT-X-DISCONTINUITY")
        i += 1
        for line in valid_lines:
            first_lines.insert(i, line)
            i += 1

        return "\n".join(first_lines)

    def __init__(self, video_folder: os.PathLike, premium_qualities=[TEN_EIGHTY_P]):
        threading.Thread.__init__(self)

        self.videos = os.listdir(video_folder)
        self.video_folder = video_folder

        self.reset_lists()

        self.premium_qualities = premium_qualities

        self.media_sequence = 0

        self.list_length = 0

    def reset_lists(self):
        self.playlists: dict[str, str] = {}
        self.playlists[Streamer.THREE_SIXTY_P] = MEDIA_PLAYLIST_TEMPLATE.format(target_duration=Streamer.TARGET_DURATION, components="")
        self.playlists[Streamer.SEVEN_TWENTY_P] = MEDIA_PLAYLIST_TEMPLATE.format(target_duration=Streamer.TARGET_DURATION, components="")
        self.playlists[Streamer.TEN_EIGHTY_P] = MEDIA_PLAYLIST_TEMPLATE.format(target_duration=Streamer.TARGET_DURATION, components="")

    def update_media_sequences(self):
        for quality in self.playlists.keys():
            MEDIA_SEQUENCE_MARKER = "#EXT-X-MEDIA-SEQUENCE:"
            found = self.playlists[quality].find(MEDIA_SEQUENCE_MARKER)
            end = min(self.playlists[quality].find("\n", found), self.playlists[quality].find(",", found))
            self.playlists[quality] = self.playlists[quality][:found+len(MEDIA_SEQUENCE_MARKER)] + str(self.media_sequence) + self.playlists[quality][end:]

    def remove_first(self):
        MEDIA_FILE_MARKER = "#EXTINF:"
        DISCONTINUITY_MARKER = "#EXT-X-DISCONTINUITY"
        for quality in self.playlists.keys():
            playlist = self.playlists[quality]

            found = playlist.find(MEDIA_FILE_MARKER)
            discontinuity = playlist.find(DISCONTINUITY_MARKER)

            if discontinuity > 0 and discontinuity < found:
                #Delete three lines from continuity marker, if there is one
                end = playlist.find("\n", playlist.find("\n", playlist.find("\n", discontinuity) + 1) + 1)
                playlist = playlist[:discontinuity] + playlist[end+1:]
            else:
                #Otherwise just two
                end = playlist.find("\n", playlist.find("\n", found) + 1)
                playlist = playlist[:found] + playlist[end+1:]

            self.playlists[quality] = playlist
    def broke(self) -> bool:
        if self.playlists["360"].count("#EXTM3U") > 1:
            return True
        return False
    def run(self):
        while True:
            if self.list_length >= self.TARGET_LIST_LENGTH:
                for i in range(self.list_length - self.TARGET_LIST_LENGTH + 1):
                    self.remove_first()
                    self.list_length -= 1
                    self.media_sequence += 1
                    self.update_media_sequences()

            if self.list_length <= self.TARGET_LIST_LENGTH:
                video = secrets.choice(self.videos)
                for quality in self.playlists.keys():
                    with open(self.video_folder+video+f'/{quality}/{quality}_video.m3u8') as f:
                        segment_playlist = f.read()
                        segment_playlist = Streamer.__add_basepath__(segment_playlist, os.path.join(os.path.join(self.video_folder, video),quality))
                        self.playlists[quality] = Streamer.__append_lists__(self.playlists[quality], segment_playlist)
                num_new_segments = segment_playlist.count("#EXTINF:")
                self.list_length += num_new_segments

            time.sleep(Streamer.TARGET_DURATION)

    def get_media_playlist(self, quality=THREE_SIXTY_P) -> str:
        return self.playlists[quality]

    def get_master_playlist(self, premium=False) -> str:
        if premium:
            return MASTER_PLAYLIST

        cleaned_lines = []
        lines = MASTER_PLAYLIST.splitlines()
        for i in range(len(lines)):
            for premium_quality in self.premium_qualities:
                if lines[i] != premium_quality+".m3u8":
                    cleaned_lines.append(lines[i])
                else:
                    cleaned_lines.pop()

        return "\n".join(cleaned_lines)

if __name__ == "__main__":
    BASE_PATH = "/home/shayanbahrainy/Videos/Nature vids/converted/"
    streamer = Streamer(BASE_PATH)
    vid1 = secrets.choice(streamer.videos)
    vid2 = secrets.choice(streamer.videos)
    with open(BASE_PATH+vid1+"/360/360_video.m3u8") as f:
        vid1_list = f.read()
    with open(BASE_PATH+vid2+"/360/360_video.m3u8") as f:
        vid2_list = f.read()
    print("Duration of individual lists: " + str(streamer.__calculate_target_dur__(vid1_list)) + " " + str(streamer.__calculate_target_dur__(vid2_list)))
    combined_list = streamer.__append_lists__(vid1_list, vid2_list)
    new_duration = streamer.__calculate_target_dur__(combined_list)
    print("Duration of both lists: " + str(new_duration))

    print("\n" * 3 + "List before updating duration: " + combined_list)
    combined_list = streamer.__replace_target_dur__(combined_list, new_duration)
    print("\n" * 3 + "List after: " + combined_list)
    print("\n" + "Detecting duration: " + str(streamer.__get_list_dur__(combined_list)))