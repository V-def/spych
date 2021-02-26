"""download from youtube video and subtitles"""
from logs import YoutubeDownloaderLogger
import youtube_dl


class Download:
    """download class"""

    def __init__(self, arg):
        self.url = None
        self.file_name = None
        self.temp = None

        if arg.startswith('http'):
            self.url = arg
        else:
            self.search(arg)

    def search(self, query):
        """search an url with a string"""
        from youtubesearchpython import VideosSearch

        response = VideosSearch(query, limit=1)

        self.url = response.result()["result"][0]["link"]

    def hook(self, d):
        """hook that save the file name"""
        if d["status"] == 'finished':
            self.file_name = d["filename"]

    def ydl(self):
        """download the video and the subtitles"""
        ydl_opts = {
            'outtmpl': '/videos/%(title)s/%(title)s.%(ext)s',  # output file path and name
            'logger': YoutubeDownloaderLogger(),  # logger class
            'progress_hooks': [self.hook],
            'ignoreerrors': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'allsubtitles': True
                    }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
