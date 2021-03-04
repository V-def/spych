"""subtitles"""
import wave
import contextlib
import pandas as pd


class Subtitles:
    """subtitles class"""

    def __init__(self, file, default_language='en'):
        self.file = file
        self.path = f'{self.file.path}/subtitles'
        self.language = default_language
        self.df = pd.DataFrame(columns=["n", "time", "text"]).set_index("n")

        self.generated = False

        self.boot()

    def boot(self):
        self.set_language()
        self.read()

    def read(self):
        """read the subtitle file and convert it into table"""
        if self.file:
            with open(str(self.file), 'r', encoding='utf-8-sig') as f:
                if self.file.extension == '.vtt':
                    for n, sequence in enumerate(f.read().split('\n\n')[1:]):
                        temp = sequence.split('\n')
                        time = temp[0].split(' --> ')
                        text = ' '.join(temp[1:])
                        self.append({"time": time, "text": text})

                elif self.file.extension == '.srt':
                    for sequence in f.read().split('\n\n'):
                        temp = sequence.split('\n')
                        n = int(temp[0])
                        time = temp[1].split(' --> ')
                        text = ' '.join(temp[2:])
                        self.append({"n": n, "time": time, "text": text})
                else:
                    raise Exception(f'unknown subtitle format : "{self.file.extension}"')
        else:
            raise FileNotFoundError(f'cannot find {self.file}')

        self.update_df()

    def append(self, subtitle):
        if subtitle["time"] != '' and subtitle["text"] != '':
            self.df = self.df.append(subtitle, ignore_index=True)

    def update_df(self):
        """update the dataframe by creating calculated columns"""
        self.df["words"] = self.df["text"].apply(self.count_words)
        self.df["duration"] = self.df["time"].apply(self.get_duration_timestamp)

    def set_language(self):
        """update the language using the file sub extension"""
        temp = self.file.name.split('.')
        self.language = temp[-1] if len(temp) > 1 else self.language

    def speech(self, mode='pyttsx3', depth=2):
        """convert table into speech in mp3"""
        if mode == 'pyttsx3':
            self.speech_pyttsx3(depth)
        elif mode == 'gtts':
            self.speech_gtts()

    def speech_pyttsx3(self, depth=2):
        """convert table into speech in mp3 using pyttsx3 module
        conversion is made locally"""
        import pyttsx3

        self.init_pyttsx3()
        engine = pyttsx3.init()
        engine.setProperty('voice',
                           "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0")
        # change property about engine here for

        for sequence in self:
            # change property about engine locally here
            engine.setProperty('rate', sequence.rate)
            engine.save_to_file(text=sequence.text, filename=self.get_file(sequence[0]))

        engine.runAndWait()

        self.grade_pyttsx3()

        if depth > 0:
            self.speech_pyttsx3(depth=depth-1)

        self.generated = True

    def grade_pyttsx3(self):
        self.df["recorded"] = self.df.apply(self.get_record, axis=1)
        self.df["ratio"] = self.df["recorded"] / self.df["duration"]

    def init_pyttsx3(self):
        if 'ratio' in self.df:
            self.df["rate"] = self.df["rate"] * self.df["ratio"]
        else:
            self.df["rate"] = 150

    def speech_gtts(self, preprocess=True):
        """convert table into speech in mp3 using gtts module
        warning : uses internet to request google translate"""
        from gtts import gTTS
        from gtts.tokenizer import pre_processors

        if preprocess:
            self.df["text"] = self.df["text"].apply(pre_processors.word_sub)

        for sequence in self:
            speech = gTTS(text=sequence.text, lang=self.language, slow=False)
            speech.save(self.get_file(sequence[0]))

        self.generated = True

    def get_record(self, series):
        return self.get_duration_file(self.get_file(n=series.name))

    def get_file(self, n):
        return f'{self.path}/seq-{n}.mp3'

    @staticmethod
    def get_duration_file(file):
        with contextlib.closing(wave.open(file, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    @staticmethod
    def get_duration_timestamp(timestamp):
        return Subtitles.time_from_string(timestamp[1]) - Subtitles.time_from_string(timestamp[0])

    @staticmethod
    def time_from_string(element):
        h, m, s = [float(e) for e in element.split(':')]
        return 60 * 60 * h + 60 * m + s

    @staticmethod
    def count_words(text, space_chars=(" ", "-", "'")):
        """return the number of words from the text string"""
        for char in space_chars:
            text = text.replace(char, " ")
        return len(text.split(' '))

    def __iter__(self):
        """allows to iter self"""
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
