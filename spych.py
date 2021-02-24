"""spych module"""
from files import File, Setup
from subtitles import Subtitles
from video import Video


class Spych:
    """Spych class"""

    def __init__(self, video_file, subtitle_file):
        self.video = Video(File(video_file))
        self.subtitles = Subtitles(File(subtitle_file))

        self.directory = self.video.file.name
        setup = Setup(self.directory)
        setup.create_directory()

    def process(self):
        """do the video montage of all audio clips at the right spots and export it to the folder"""
        from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

        video = VideoFileClip(str(self.video.file))

        subtitles = self.subtitles.list

        audios = []
        for subtitle in subtitles:
            subtitle_audio = AudioFileClip(f'videos/{self.directory}/subtitles/seq-{subtitle["n"]}.mp3')
            t = subtitle["time"][0]
            audios.append(subtitle_audio.set_start(t))

        main_audio = CompositeAudioClip(audios)

        video.audio = main_audio
        video.write_videofile(f"videos/{self.directory}/output.mp4")
