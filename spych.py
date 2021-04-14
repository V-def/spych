# -*- coding: utf-8 -*-
"""
This module implements the core developer interface for Spych.
"""
from download import Download
from files import Directory, File, create_video_directory, video_directory, search
from subtitles import Subtitles
from video import Video


class Spych:
    """Core developer interface for Spych."""

    def __init__(self, query: str='',
                 download: Download=None, directory: Directory=None, video: Video=None, subtitles: Subtitles=None,
                 directory_name: str='', video_name: str='', subtitles_name: str ='',
                 language: str='en', video_language: str='en', res: int=0, output_name: str ='Output-{name}{ext}',
                 autoprocess: bool=True):
        """
        Construct a :class:`Spych <Spych>`.

        one of the 8 first arguments is required

        :param str query:
            youtube search terms
        :param Download download:
            Download object of a search
        :param Directory directory:
            Directory object of the directory that contains the video/subtitles
        :param Video video:
            Video object with the video file
        :param Subtitles subtitles:
            Subtitles object with the subtitles file

        :param str directory_name:
            the name of the directory that contains the video/subtitles
        :param str video_name:
            the name of the video file
        :param str subtitles_name:
            the name of the subtitles file

        :param str language:
            language of the output
        :param str video_language:
            language of the video input
        :param int res:
            resolution of the video 0 the worst, -1 the best
        :param str output_name:
            the name of the output file
        :param autoprocess:
            automatically process the speech and editing when call
        """

        self.directory = None
        self.video = None
        self.subtitles = None
        self.lang = language
        self.output_name = output_name

        create_video_directory()

        self.find_directory(directory=directory, directory_name=directory_name)

        if query or download:
            if not download:
                download = self.create_download(
                    query=query, video_language=video_language,
                    directory=self.directory, video_name=video_name, subtitles_name=subtitles_name)
            self.download(download, res=res)
        else:
            self.find(video=video, video_name=video_name, subtitles=subtitles, subtitles_name=subtitles_name)

        self.update_output_name()

        if autoprocess:
            self.process()

    def find_directory(self, directory: Directory=None, directory_name: str=None):
        """
        finds the directory based on an directory object or the name of the directory and saves it in self.directory
        :param Directory directory:
            Directory object of the targeted directory
        :param str directory_name:
            name of the targeted directory
        """

        if type(directory) is Directory:
            self.directory = directory
        elif directory:
            raise TypeError(f'directory must be Directory, not {type(directory).__name__}')
        elif directory_name:
            self.directory = video_directory(directory_name=directory_name, find=True, create=True)

    def find_video(self, video: Video=None, video_name: str=None):
        """
        finds the video file based on an video object or the name of the video file and saves it in self.video
        :param Video video:
            Video object of the targeted video
        :param str video_name:
            name of the targeted video
        """
        if type(video) is Video:
            self.video = video
        elif type(video) is File:
            self.video = Video(File(video))
        elif video is None:
            if video_name:
                path = str(self.directory) if self.directory else '.'
                self.video = Video(search(path=path, name=video_name, extension_type='video', raise_error=True))
            elif self.directory:
                self.video = Video(search(path=str(self.directory), extension_type='video', raise_error=True))
            else:
                raise TypeError(f'argument query, download, directory, video or video_name missing')
        else:
            raise TypeError('video argument type must be Video, File or None')

        if not self.directory:
            self.find_directory(Directory(self.video.file))

    def find_subtitles(self, subtitles: Subtitles=None, subtitles_name: str=None):
        """
        finds the subtitles file based on an subtitles object or the name of the subtitles file
        and saves it in self.subtitles
        :param Subtitles subtitles:
            Subtitles object of the targeted subtitles
        :param str subtitles_name:
            name of the targeted subtitles
        """
        if type(subtitles) is Subtitles:
            self.subtitles = subtitles
        elif type(subtitles) is File:
            self.subtitles = Subtitles(File(subtitles))
        elif subtitles is None:
            if subtitles_name:
                path = str(self.directory) if self.directory else '.'
                file = search(path=path, name=subtitles_name, extension_type='subtitles', raise_error=False)
                if file:
                    self.subtitles = Subtitles(file)
            elif self.directory:
                file = search(path=str(self.directory), name=None, extension_type='subtitles', raise_error=False)
                if file:
                    self.subtitles = Subtitles(file)
        else:
            raise TypeError('subtitles argument type must be Subtitles, File or None')

    def create_download(self, query: str, video_language: str, directory: Directory or None,
                        video_name: str, subtitles_name: str):
        """
        create a Download object based on the Spych informations
        :param str query:
            youtube search terms
        :param str video_language:
            language of the video input
        :param Directory directory:
            Directory object of the directory that contains the video/subtitles
        :param str video_name:
            the name of the video file
        :param str subtitles_name:
            the name of the subtitles file
        :return: Download object
        """
        return Download(query, langs=(self.lang, video_language), directory=directory,
                        video_name=video_name, subtitles_name=subtitles_name)

    def download(self, download: Download, res: int):
        """
        download video and subtitles if possible from youtube using the download object
        :param Download download:
            Download object of a search
        :param int res:
            resolution of the video 0 the worst, -1 the best
        """
        download.dl(res=res)
        self.directory = download.directory
        self.find(video_name=download.video_file.name, subtitles_name=download.subtitles_file.name)

    def find(self, video: Video=None, video_name: str=None, subtitles: Subtitles=None, subtitles_name: str=None):
        """
        finds the video and the subtitles
        :param Video video:
            Video object of the targeted video
        :param str video_name:
            name of the targeted video
        :param Subtitles subtitles:
            Subtitles object of the targeted subtitles
        :param str subtitles_name:
            name of the targeted subtitles
        """
        self.find_video(video=video, video_name=video_name)
        self.find_subtitles(subtitles=subtitles, subtitles_name=subtitles_name)

    def update_output_name(self):
        """
        update the output name of the video based on the known informations such as the title and the extension
        """
        output_vars = {'{name}': self.video.file.name, '{ext}': self.video.file.extension}
        for key in output_vars:
            self.output_name = self.output_name.replace(key, output_vars[key])

    def speech(self, mode: str='pyttsx3', depth: int=2):
        """
        create the speeches using subtitles.speech()
        :param str mode:
            "pyttsx3" or "gtts"
        :param int depth:
            the number of recursions
        """
        self.subtitles.speech(mode=mode, depth=depth)
        print(f'Successfully recorded the voice using {mode}')

    def edit(self, correct_speed: bool=False):
        """
        do the video montage of all audio clips at the right spots and export it to the folder in the self.output_name
        :param correct_speed:
            speed up or slow down the clips if they are not at the right speed
            warning : causes ton change
        """
        import moviepy.editor as mpy

        print('Preprocessing the speeches of the video')

        if not self.subtitles:
            print("Warning speeches files not generated yet")

        video = mpy.VideoFileClip(str(self.video.file))

        audios = []
        for sequence in self.subtitles:
            try:
                if sequence.recorded > 0 and not sequence.text.startswith('#'):
                    subtitle_audio = mpy.AudioFileClip(self.subtitles.get_file(sequence.Index))
                else:
                    continue
            except OSError:
                raise FileNotFoundError("audio files missing, did you started the subtitle.speech method ?")

            if correct_speed:
                subtitle_audio = subtitle_audio.fx(mpy.vfx.speedx, subtitle_audio.duration/sequence.duration)

            audios.append(subtitle_audio.set_start(sequence.time[0]))

        print("Composing the speeches together")

        main_audio = mpy.CompositeAudioClip(audios)

        print(f'Editing the video {self.video.file.name} to match the video with voices')

        video.audio = main_audio

        print(f'Saving the video {self.video.file.name}')
        video.write_videofile(f"{self.directory}\\{self.output_name}")

    def process(self):
        """
        auto process the spych
        does the speech and the editing
        """
        self.speech()
        self.edit()

    def __repr__(self):
        return f'Spych(video_file={self.video.file}, subtitles_file={self.subtitles.file}, directory={self.directory})'
