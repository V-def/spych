"""spych module"""
from download import Download
from files import File, Setup
from subtitles import Subtitles
from video import Video


class Spych:
    """Spych class"""

    def __init__(self, quarry=None, video_file=None, subtitle_file=None, directory=None):
        self.video = None
        self.subtitles = None
        self.setup = None

        if quarry:
            self.download(quarry=quarry)
        elif video_file and subtitle_file:
            self.detect_from_files(video_file=video_file, subtitle_file=subtitle_file, directory=directory)
        elif directory:
            self.detect_from_directory(directory=directory, video_file=video_file, subtitle_file=subtitle_file)

    def detect_from_files(self, video_file, subtitle_file, directory=None):
        self.video = Video(File(video_file))
        self.subtitles = Subtitles(File(subtitle_file))

        if not directory:
            directory = self.video.file.name
        self.start_setup(directory)

    def detect_from_directory(self, directory, video_file=None, subtitle_file=None):
        self.start_setup(directory)

        if not video_file:
            video_file = self.setup.search(path=self.setup.path, name=directory, extension='video')[0]
            # take first element but it can have multiple files

        if not subtitle_file:
            subtitle_file = self.setup.search(path=self.setup.path, name=directory, extension='subtitles')[0]

        self.video = Video(video_file)
        self.subtitles = Subtitles(subtitle_file)

    def download(self, quarry):
        """download video and subtitles if possible from youtube"""
        download = Download(quarry)

        self.start_setup(download.name)  # create

        print(f'Downloading the video "{download.name}" from {download.url}')
        download.ydl()
        print(f'The video {download.name} has been downloaded')

        file = File(download.file_name)

        self.start_setup(file.name)

        self.video = Video(File(file))

        subtitle_files = self.setup.search(file.path, file.name, 'subtitles')
        if subtitle_files:
            self.subtitles = Subtitles(File(subtitle_files[0]))
        else:
            raise FileNotFoundError(f'Cannot find any subtitles file in {file.path}')

    def start_setup(self, directory):
        self.setup = Setup(directory)
        self.setup.create_directory()

    def speech(self, mode='pyttsx3', depth=2):
        self.subtitles.speech(mode=mode, depth=depth)

    def process(self, correct_speed=False):
        """do the video montage of all audio clips at the right spots and export it to the folder"""
        import moviepy.editor as mpy

        if not self.subtitles:
            print("Warning files not generated yet")

        video = mpy.VideoFileClip(str(self.video.file))

        audios = []
        for sequence in self.subtitles:
            try:
                subtitle_audio = mpy.AudioFileClip(self.subtitles.get_file(sequence.Index))
            except OSError:
                raise FileNotFoundError("audio files missing, did you started the subtitle.speech method ?")

            if correct_speed:
                subtitle_audio = subtitle_audio.fx(mpy.vfx.speedx, subtitle_audio.duration/sequence.duration)

            audios.append(subtitle_audio.set_start(sequence.time[0]))

        main_audio = mpy.CompositeAudioClip(audios)

        video.audio = main_audio
        video.write_videofile(f"{self.setup.path}/Output {self.video.file.name}.mp4")
