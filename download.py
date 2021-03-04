"""download from youtube video and subtitles"""
from logs import YoutubeDownloaderLogger
import youtube_dl


class Download:
    """download class"""

    def __init__(self, quarry):
        self.url = None
        self.name = None
        self.file_name = None

        self.search(quarry)

    def search(self, quarry):
        """search an url with a string"""
        from youtubesearchpython import VideosSearch

        response = VideosSearch(quarry, limit=1)

        if len(response.result()["result"]) == 0:
            raise Exception(f'did not find any videos named {quarry}')

        infos = response.result()["result"][0]

        self.url = infos["link"]
        self.name = infos["title"]
        self.name = "".join(e for e in self.name if e.isascii() and e not in '\/:*?"<>|').replace('.', ' ')

        while self.name.endswith(' '):  # to avoid problems when creating a directory
            self.name = self.name[:-1]

    def hook(self, d):
        """hook that save the file name"""
        if d["status"] == 'finished':
            self.file_name = d["filename"]

    def ydl(self):
        """download the video and the subtitles"""

        YoutubeDownloaderLogger().reset()  # reset log file

        ydl_opts = {
            'outtmpl': f'/videos/{self.name}/{self.name}.%(ext)s',  # output file path and name
            'logger': YoutubeDownloaderLogger(),  # logger class
            'progress_hooks': [self.hook],
            'ignoreerrors': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'allsubtitles': True
                    }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not self.file_name:
            raise Exception(f'cannot download {self.url}')
