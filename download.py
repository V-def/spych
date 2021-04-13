"""search and download from youtube video and subtitles"""
from pytube import YouTube
from pytube.helpers import safe_filename
from files import SpychDirectory
from random import choice
import unicodedata


class Download:
    """download class"""

    def __init__(self, query: str, langs=('en', 'fr')):
        self.url = None
        self.langs = list(langs)
        self.yt = None
        self.directory = None
        self.name = None
        self.subtitles = None
        self.videos = None

        self.video_downloaded = False
        self.subtitle_downloaded = False

        self.search(query)

    def search(self, query: str):
        """search an url with a string"""
        from youtubesearchpython import VideosSearch

        response = VideosSearch(query, limit=1)

        if len(response.result()["result"]) == 0:
            raise Exception(f'did not find any videos named {query}')

        if not self.langs:
            self.langs.append(response.language)

        infos = response.result()["result"][0]

        self.url = infos["link"]
        self.yt = YouTube(self.url)
        self.name = safe_filename(self.yt.title)
        print(f'Video {self.name} ({self.url}) found')

        self.directory = SpychDirectory(self.name, create=True)

    def dl(self, lang_code=None, itag=None, file_extension='mp4', skip_existing=True, res=0):
        if not (skip_existing and self.subtitle_downloaded):
            self.subtitle(lang_code=lang_code)
        if not (skip_existing and self.video_downloaded):
            self.video(itag=itag, only_video=self.subtitle_downloaded, file_extension=file_extension, skip_existing=skip_existing, res=res)

    def get_videos(self, only_video=True, file_extension='mp4', full_disp=True):
        self.videos = self.yt.streams.filter(
            only_video=only_video,
            file_extension=file_extension
        ).order_by('resolution')
        print(f'Found {len(self.videos)} video files for "{self.name}"')
        if full_disp:
            for n, video in enumerate(self.videos):
                print(f'{video.type} {n+1}: '
                      f'itag={video.itag} '
                      f'res={video.resolution} '
                      f'fps={video.fps} '
                      f'extension={video.subtype} '
                      f'audio={video.includes_audio_track}')

    def video(self, itag=None, only_video=True, file_extension='mp4', skip_existing=True, res=0):
        """download video"""

        print(f'Downloading the video "{self.name}" from {self.url}')

        if not self.videos:
            self.get_videos(only_video=only_video, file_extension=file_extension, full_disp=False)

        if itag:
            video = self.videos.itag_index[itag]
        else:
            video = self.videos[res]

        video.download(output_path=str(self.directory), filename=self.directory.name, skip_existing=skip_existing)

        self.video_downloaded = True

        print(f'The video {self.name} has been downloaded')

    def get_subtitles(self, full_disp=True):
        """get the list of all subtitles"""
        self.subtitles = self.yt.captions
        print(f'Found {len(self.subtitles)} subtitles files')
        if full_disp:
            for n, subtitle in enumerate(self.subtitles):
                print(f'subtitle {n+1}: '
                      f'code={subtitle.code} '
                      f'name="{subtitle.name}"')

    def subtitle(self, lang_code=None):
        """download subtitles"""

        if not self.subtitles:
            self.get_subtitles(full_disp=False)

        subtitle = None
        codes = ([lang_code] if lang_code else [])
        codes = codes + self.langs + [f'a.{l}' for l in self.langs]
        if self.subtitles:
            for code in codes:
                try:
                    subtitle = self.subtitles[code]
                    print(f'Caption {subtitle.name} ({subtitle.code}) found and selected (matching language {code})')
                    break

                except KeyError:
                    pass

            if not subtitle:
                subtitle = choice(list(self.subtitles))
                print(f'Warning languages not found, choosing first caption : {subtitle.name} ({subtitle.code})')

            with open(f'{self.directory}\\{self.directory.name}.srt', 'w', encoding='utf-8') as f:
                caption_string = unicodedata.normalize("NFKD", subtitle.generate_srt_captions())
                f.write(caption_string)

            self.subtitle_downloaded = True

            print(f'The subtitles {subtitle.name} has been downloaded')

        else:
            print(f'No subtitles found for the video {self.name}')

    def __repr__(self):
        return f'Download(name={self.name}, url={self.url}, langs={self.langs})'
