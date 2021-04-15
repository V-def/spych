# -*- coding: utf-8 -*-
"""
Subtitles file include Subtitles class who process everything related to subtitles
"""
import wave
import contextlib
import pandas as pd
from files import subtitle_directory
import unicodedata
import re


class Subtitles:
    """Subtitles class which allows tools with subtitles and text to speech from subtitles"""

    def __init__(self, file, language: str='en'):
        """
        Construct a :class:`Subtitles <Subtitles>`.
        :param File file:
            File object of the subtitles
        :param str language:
            language of the output
        """
        self.file = file
        self.directory = subtitle_directory(self.file.path, find=False, create=True)
        self.language = language
        self.df = pd.DataFrame(columns=["n", "time", "text"]).set_index("n")

        self._engine = None

        self.generated = False
        self.boot()

    @property
    def engine(self):
        if not self._engine:
            import pyttsx3
            self._engine = pyttsx3.init()
        return self._engine

    def boot(self):
        """boot the Subtitle object"""
        self.set_language()
        self.read()

    def read(self):
        """read the subtitle file and convert it into a dataframe"""
        if self.file:
            with open(str(self.file), 'r', encoding='utf-8-sig') as f:
                subtitles_string = f.read()

            if self.file.extension == '.vtt':
                for n, sequence in enumerate(subtitles_string.split('\n\n')[1:]):
                    temp = sequence.split('\n')
                    time = [t.replace(',', '.') for t in temp[0].split(' --> ')]
                    text = ' '.join(temp[1:])
                    self.append({"time": time, "text": text})

            elif self.file.extension == '.srt':
                for sequence in subtitles_string.split('\n\n'):
                    temp = sequence.split('\n')
                    time = [t.replace(',', '.') for t in temp[1].split(' --> ')]
                    text = ' '.join(temp[2:])
                    self.append({"time": time, "text": text})
            else:
                raise Exception(f'unknown subtitle format : "{self.file.extension}"')
        else:
            raise FileNotFoundError(f'cannot find {self.file}')

        self.update_df()

    def append(self, subtitle):
        """append the dataframe of subtitles"""
        if subtitle["time"] != '' and subtitle["text"] != '':
            self.df = self.df.append(subtitle, ignore_index=True)

    def update_df(self):
        """update the dataframe by creating new columns based on the default ones"""

        # normalize the text to avoid problems on speech
        self.df["text"] = self.df["text"].apply(lambda t: unicodedata.normalize('NFC', t))

        # count words
        self.df["words"] = self.df["text"].apply(self.count_words)

        # duration
        self.df["duration"] = self.df["time"].apply(self.get_duration_timestamp)

    def set_language(self):
        """update the language using the file subtitle extension"""
        temp = self.file.name.split('.')
        self.language = temp[-1] if len(temp) > 1 else self.language

    def speech(self, mode='pyttsx3', depth: int=2):
        """convert dataframe into mp3 speeches files"""
        if mode == 'pyttsx3':
            self.speech_pyttsx3(depth)
        elif mode == 'gtts':
            self.speech_gtts()
        else:
            raise Exception(f'unknown mode : {mode}')

    def speech_pyttsx3(self, depth: int=2):
        """
        convert dataframe into mp3 speeches files using pyttsx3 module
        conversion is made locally
        :param int depth:
            number of recursions
        """
        self.init_pyttsx3()

        for sequence in self:
            # change property about engine locally here
            self.engine.setProperty('rate', sequence.rate)
            self.engine.save_to_file(text=sequence.text, filename=self.get_file(sequence[0]), name=str(sequence.index))

        self.engine.runAndWait()

        self.grade_pyttsx3()

        if depth > 0:
            self.speech_pyttsx3(depth=depth-1)

        self.generated = True

    def grade_pyttsx3(self):
        """update the dataframe using recored files informations"""
        self.df["recorded"] = self.df.apply(self.get_record, axis=1)
        self.df["ratio"] = self.df["recorded"] / self.df["duration"]

    def init_pyttsx3(self):
        """update the dataframe using recored files informations"""
        if 'ratio' in self.df:
            self.df["rate"] = self.df["rate"] * self.df["ratio"]
        else:
            self.df["rate"] = 150

    def speech_gtts(self, preprocess: bool=True):
        """
        convert dataframe into mp3 speeches files using gTTs module
        conversion is made using requests to google translate
        :param bool preprocess:
            preprocess the text before rendering it to speech
        """
        from gtts import gTTS
        from gtts.tokenizer import pre_processors

        if preprocess:
            self.df["text"] = self.df["text"].apply(pre_processors.word_sub)

        for sequence in self:
            speech = gTTS(text=sequence.text, lang=self.language, slow=False)
            speech.save(self.get_file(sequence[0]))

        self.generated = True

    def get_record(self, series) -> float:
        """
        get the length of the corresponding recorded speech file from a series object of the dataframe
        :param series:
        """
        return self.get_duration_file(self.get_file(n=series.name))

    def get_file(self, n: int) -> str:
        """
        get the name of the corresponding recorded speech file from the number of the row in the dataframe
        :param n:
        """
        return f'{self.directory}\\seq-{n}.mp3'

    @staticmethod
    def get_duration_file(file) -> float:
        """
        get the duration of an audio file
        :param file:
            file full name
        :return float:
            duration
        """
        with contextlib.closing(wave.open(file, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    @staticmethod
    def get_duration_timestamp(timestamp):
        """
        get the time of a timestamp in seconds
        :param timestamp:
        :return: duration
        """
        return Subtitles.time_from_string(timestamp[1]) - Subtitles.time_from_string(timestamp[0])

    @staticmethod
    def time_from_string(element: str):
        """
        convert a str time '00:00:00.000' into a float in seconds
        :param str element:
            string of the time
        :return float:
            time in seconds
        """
        h, m, s = [float(e) for e in element.split(':')]
        return 60 * 60 * h + 60 * m + s

    @staticmethod
    def count_words(text: str) -> int:
        """
        return the number of words from the text string
        :param str text:
            input text
        :return:
            number of words in text
        """
        return len(re.findall(r'\S+', text))  # \S+ -> one or more non-whitespace characters

    def __iter__(self):
        """allows to iter self as it iter the rows of the dataframe"""
        return self.df.itertuples()

    def __getitem__(self, i):
        """get the sequence number i"""
        return self.df.iloc[i]

    def __len__(self):
        """get the number of sequences"""
        return self.df.shape[0]

    def __bool__(self):
        """returns if the subtitles voices has been recorded"""
        return self.generated

    def __repr__(self):
        return f'Subtitles(file={self.file}, directory={self.directory}, lang={self.language}, gen={self.generated})'
